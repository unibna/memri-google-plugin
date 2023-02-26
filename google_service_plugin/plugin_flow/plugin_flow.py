import logging
from time import time, sleep
from google_service_plugin.data.schema import Plugin, PluginRun, Account
from pymemri.pod.client import PodClient


RUN_IDLE = 'idle'                           #1
RUN_INITIALIZED = 'initilized'              #2
RUN_USER_ACTION_NEEDED = 'userActionNeeded' # 2-3
RUN_USER_ACTION_COMPLETED = 'ready'         # 2-3
RUN_STARTED = 'start'                       #3
RUN_FAILED = 'error'                        # 3-4
RUN_COMPLETED = 'done'                      #4

RUN_STATE_POLLING_INTERVAL = 0.6
RUN_USER_ACTION_TIMEOUT = 120

logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s')


# A draft class to be inherited by the actual plugin class, to handle plugin flows like auth, state, progress...
# Requires the plugin class to have a "run" method.
class PluginFlow:

    def __init__(self, client, plugin_id=None, run_id=None):
        self.client: PodClient = client
        self.run_id = run_id
        self.plugin_id = plugin_id
        self._setup_schema()
        self.initialized()

    def start(self):
        """ Plugin run wrapper - sets status and allows daemon mode intervals """   
        logging.warning('Running')
        self.started()

        while True:
        
            # Plugin class provides this method - plugin's main run logic
            self.run()
            
            # daemon run interval
            run = self.get_run(expanded=False)
            if not run.interval: # interval is falsy. To terminate, set run.interval = 0 or None
                break
            sleep(run.interval)

        self.completed()

    # =======================================
    # ---------- PLUGIN METHODS -------------

    def get_account_from_plugin(self, service=None):
        # Update plugin
        plugin = self.client.get(self.plugin_id)
        # get its connected accounts
        account_edges = plugin.get_edges('account')
        # if multiple accounts are used
        if len(account_edges) > 1 and service:
            for account_edge in account_edges:
                account = account_edge.traverse(plugin)
                if account.service == service:
                    return account
        # assumes there is only one account
        elif len(account_edges) == 1:
            return account_edges[0].traverse(plugin)       

    def ask_user_for_accounts(self, service, view, oauth_url=None):
        # start userActionNeeded flow
        vars = {
            'state': RUN_USER_ACTION_NEEDED,
            'oAuthUrl': oauth_url
        }
        self._set_run_vars(vars)
        self._set_run_view(view)

        # poll here
        start_time = time()
        # handle timeouts
        while RUN_USER_ACTION_TIMEOUT > time() - start_time:
            sleep(RUN_STATE_POLLING_INTERVAL)
            run_state = self._get_run_state()

            if run_state == RUN_USER_ACTION_COMPLETED:
                # Now the client has set up the account as an edge to the plugin
                return self.get_account_from_plugin(service=service)

        raise Exception("PluginFlow: User input timeout")

    def set_account_vars(self, vars_dictionary, service=None):
        account = self.get_account_from_plugin(service=service)
        if account:
            for k,v in vars_dictionary.items():
                setattr(account, k, v)
            self.client.update_item(account)
            logging.warning(f"ACCOUNT updated: {account.__dict__}")
        else:
            # Create account item
            account = Account(**vars_dictionary)
            # Save accounts as an edge to the plugin
            self.client.create(account)
            logging.warning(f"ACCOUNT created: {account.__dict__}")
            # add the account to the plugin item
            plugin = self.client.get(self.plugin_id)
            plugin.add_edge('account', account)
            plugin.update(self.client)

    # =======================================
    # ---------- USER CLIENT METHODS -------------

    def install_plugin(self, name, containerImage, views=[]):
        plugin = Plugin(name=name, containerImage=containerImage)
        self.client.create(plugin)
        # set in instance
        self.plugin_id = plugin.id
        # add cvus here
        for view in views:
            self.client.create(view)

        # start_plugin.view = createLoginCVUs()
        return plugin

    def trigger_plugin(self, interval=None):
        plugin = self.client.get(self.plugin_id)
        starter = PluginRun(targetItemId=self.plugin_id, containerImage=plugin.containerImage, state=RUN_IDLE, interval=interval)
        # add cvus here
        self.client.create(starter)
        self.run_id = starter.id
        print(f"Started plugin {plugin.name} - {self.plugin_id} and run id {self.run_id}")

    def terminate_run(self):
        self._set_run_vars({'interval': None})

    # =======================================
    # ---------- COMMON METHODS -------------

    def get_CVU(self, run):
        try:
            run = self.get_run(expanded=True)
            return run.get_edges('view')[0]
        except:
            return None

    def initialized(self):
        logging.warning("PLUGIN run is initialized")
        self.state = RUN_INITIALIZED
        if self.run_id:
            self._set_run_vars({'state':RUN_INITIALIZED})

    def started(self):
        logging.warning("PLUGIN run is started")
        self.state = RUN_STARTED
        if self.run_id:
            self._set_run_vars({'state':RUN_STARTED})

    def failed(self, error):
        logging.error(f"PLUGIN run is failed: {error}")
        print("Exception while running plugin:", error)
        self.state = RUN_FAILED
        if self.run_id:
            self._set_run_vars({'state':RUN_FAILED, 'message': str(error)})

    def completed(self):
        logging.warning("PLUGIN run is completed")
        self.state = RUN_COMPLETED
        if self.run_id:
            self._set_run_vars({'state':RUN_COMPLETED})

    def complete_user_action(self):
        self._set_run_vars({'state': RUN_USER_ACTION_COMPLETED})

    def is_user_action_needed(self):
        return self._get_run_state() == RUN_USER_ACTION_NEEDED

    def is_completed(self):
        return self._get_run_state() == RUN_COMPLETED

    def is_daemon(self):
        run = self.get_run(expanded=False)
        return run.interval and run.interval > 0

    def get_run(self, expanded=False):
        return self.client.get(self.run_id, expanded=expanded)


    # =======================================
    # --------- INTERNAL METHODS ------------

    def _get_run_state(self):
        start_plugin = self.get_run()
        return start_plugin.state

    def _set_run_vars(self, vars):
        start_plugin = self.client.get(self.run_id, expanded=False)
        for k,v in vars.items():
            setattr(start_plugin, k, v)
        self.client.update_item(start_plugin)

    def _set_run_view(self, view_name):
        found_cvu = None
        views = self.client.search({'type': 'CVUStoredDefinition'}) # 'name': view_name
        for v in views:
            if v.name == view_name:
                found_cvu = v
        if not found_cvu:
            logging.error("CVU is NOT FOUND")
            return

        run = self.get_run()

        bound_CVU_edge = self.get_CVU(run) # index error here if there is no already bound CVU 
        if bound_CVU_edge:
            logging.warning(f"Plugin Run already has a view. Updating with {view_name}")
            bound_CVU_edge.target = found_cvu  # update CVU
            bound_CVU_edge.update(self.client) # having doubts if this really updates the existing edge
        else:
            logging.warning(f"Plugin Run does not have a view. Creating {view_name}")
            run.add_edge('view', found_cvu)
            run.update(self.client)
    

    def _setup_schema(self):
        self.client.add_to_schema(Account)
        self.client.add_to_schema(Plugin)
        self.client.add_to_schema(PluginRun)