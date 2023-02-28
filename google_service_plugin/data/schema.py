from pymemri.data.schema import Item, Edge, File, Account, Plugin
from typing import (
    Optional,
    Any
)
    

class Account(Item):

    service: Optional[str] = None
    identifier: Optional[str] = None
    secret: Optional[str] = None
    refreshToken: Optional[str] = None
    code: Optional[str] = None
    errorMessage: Optional[str] = None
    
    def __init__(self, service=None, identifier=None, secret=None, code=None, refreshToken=None, errorMessage=None, id=None, deleted=None): #e.g. username, password or access key, secret key etc.
        super(Account, self).__init__()
        self.id = id
        self.deleted = deleted
        self.service = service
        self.identifier = identifier
        self.secret = secret
        self.refreshToken = refreshToken
        self.code = code
        self.errorMessage = errorMessage
        
    @classmethod
    def from_json(cls, json):
        id = json.get("id", None)
        deleted = json.get("deleted", None)
        service = json.get("service", None)
        identifier = json.get("identifier", None)
        secret = json.get("secret", None)
        code = json.get("code", None)
        refreshToken = json.get("refreshToken", None)
        errorMessage = json.get("errorMessage", None)

        res = cls(service=service, identifier=identifier, secret=secret, code=code, refreshToken=refreshToken, errorMessage=errorMessage, id=id, deleted=deleted)
        return res


class Plugin(Item):
    
    name: Optional[str]
    containerImage: Optional[str]
    account: Optional[Account]

    def __init__(self, name, containerImage, account=None, id=None, deleted=None):
        super(Plugin, self).__init__(id=id, deleted=deleted)
        self.name = name
        self.containerImage = containerImage
        self.account = account if account else []

    @classmethod
    def from_json(cls, json):
        id = json.get("id", None)
        deleted = json.get("deleted", None)
        name = json.get("name", None)
        containerImage = json.get("containerImage", None)
        all_edges = json.get("allEdges", None)
        
        account = []
        
        if all_edges is not None:
            for edge_json in all_edges:
                edge = Edge.from_json(edge_json)
                if edge._type == "account" or edge._type == "~account": 
                    account.append(edge)
                
        res = cls(name=name, containerImage=containerImage, account=account, id=id, deleted=deleted)
        for e in res.get_all_edges(): e.source = res
        return res


class PluginRun(Item):
    
    def __init__(self, targetItemId, containerImage, state=None, oAuthUrl=None, interval=None, view=None, id=None, deleted=None):
        super(PluginRun, self).__init__(id=id, deleted=deleted)
        self.targetItemId = targetItemId
        self.containerImage = containerImage
        self.state = state
        self.oAuthUrl = oAuthUrl
        self.interval = interval
        # CVUStoredDefinitions
        self.view = view if view else []


    @classmethod
    def from_json(cls, json):
        id = json.get("id", None)
        deleted = json.get("deleted", None)
        targetItemId = json.get("targetItemId", None)
        containerImage = json.get("containerImage", None)
        state = json.get("state", None)
        oAuthUrl = json.get("oAuthUrl", None)
        interval = json.get("interval", None)
        all_edges = json.get("allEdges", None)

        view = []

        if all_edges is not None:
            for edge_json in all_edges:
                edge = Edge.from_json(edge_json)
                if edge._type == "view" or edge._type == "~view": 
                    view.append(edge)

        res = cls(targetItemId=targetItemId, containerImage=containerImage, state=state, view=view, oAuthUrl=oAuthUrl, interval=interval, id=id, deleted=deleted)
        return res


class Image(File):
    # Attributes
    mediaItemId: Optional[str]
    productUrl: Optional[str]
    baseUrl: Optional[str]
    mimeType: Optional[str]
    creationTime: Optional[str]
    width: Optional[int]
    height: Optional[int]
    cameraMake: Optional[str]
    cameraModel: Optional[str]
    focalLength: Optional[int]
    apertureFNumber: Optional[float]
    isoEquivalent: Optional[int]
    exposureTime: Optional[str]

    def __init__(self, 
        filename=None, keystr=None,nonce=None,sha256=None,starred=None,externalId=None,
        mediaItemId=None,productUrl=None,baseUrl=None,mimeType=None,creationTime=None,
        width=None,height=None,cameraMake=None,cameraModel=None,focalLength=None,
        apertureFNumber=None,isoEquivalent=None,exposureTime=None,
    ):
        super(Image, self).__init__(filename=filename, keystr=keystr
                                    ,nonce=nonce,sha256=sha256,
                                    starred=starred,externalId=externalId)

        self.mediaItemId = mediaItemId
        self.productUrl = productUrl
        self.baseUrl = baseUrl
        self.mimeType = mimeType
        self.creationTime = creationTime
        self.width = width
        self.height = height
        self.cameraMake = cameraMake
        self.cameraModel = cameraModel
        self.focalLength = focalLength
        self.apertureFNumber = apertureFNumber
        self.isoEquivalent = isoEquivalent
        self.exposureTime = exposureTime

    @classmethod
    def from_json(cls, json):
        json["mediaItemId"] = json.get("id", None)

        return cls(
            filename=json.get('filename'),
            keystr=json.get('keystr'),
            nonce=json.get('nonce'),
            sha256=json.get('sha256'),
            starred=json.get('starred'),
            externalId=json.get('externalId'),
            mediaItemId=json.get('mediaItemId'),
            productUrl=json.get('productUrl'),
            baseUrl=json.get('baseUrl'),
            mimeType=json.get('mimeType'),
            creationTime=json.get('creationTime'),
            width=int(json.get('width', 0)),
            height=int(json.get('height', 0)),
            cameraMake=json.get('cameraMake'),
            cameraModel=json.get('cameraModel'),
            focalLength=int(json.get('focalLength', 0)),
            apertureFNumber=float(json.get('apertureFNumber', 0)),
            isoEquivalent=int(json.get('isoEquivalent', 0)),
            exposureTime=json.get('exposureTime'),
        )
    

class Video(File):
    # Attributes
    mediaItemId: Optional[str]
    productUrl: Optional[str]
    baseUrl: Optional[str]
    mimeType: Optional[str]
    creationTime: Optional[str]
    width: Optional[int]
    height: Optional[int]
    cameraMake: Optional[str]
    cameraModel: Optional[str]
    fps: Optional[float]
    status: Optional[str]

    def __init__(self, 
        filename=None, keystr=None,nonce=None,sha256=None,starred=None,externalId=None,
        mediaItemId=None,productUrl=None,baseUrl=None,mimeType=None,creationTime=None,
        width=None,height=None,cameraMake=None,cameraModel=None,fps=None,status=None,
    ):
        super(Video, self).__init__(filename=filename, keystr=keystr
                                    ,nonce=nonce,sha256=sha256,
                                    starred=starred,externalId=externalId)

        self.mediaItemId = mediaItemId
        self.productUrl = productUrl
        self.baseUrl = baseUrl
        self.mimeType = mimeType
        self.creationTime = creationTime
        self.width = width
        self.height = height
        self.cameraMake = cameraMake
        self.cameraModel = cameraModel
        self.fps = fps
        self.status = status

    @classmethod
    def from_json(cls, json):
        json["mediaItemId"] = json.get("id", None)

        return cls(
            filename=json.get('filename'),
            keystr=json.get('keystr'),
            nonce=json.get('nonce'),
            sha256=json.get('sha256'),
            starred=json.get('starred'),
            externalId=json.get('externalId'),
            mediaItemId=json.get('mediaItemId'),
            productUrl=json.get('productUrl'),
            baseUrl=json.get('baseUrl'),
            mimeType=json.get('mimeType'),
            creationTime=json.get('creationTime'),
            width=int(json.get('width', 0)),
            height=int(json.get('height', 0)),
            cameraMake=json.get('cameraMake'),
            cameraModel=json.get('cameraModel'),
            fps=float(json.get('fps', 0)),
            status=json.get('status'),
        )


class DriverFile(File):

    def __init__(self):
        pass

    @classmethod
    def from_json(self, json):
        pass


class QueueObject:

    def __init__(self, parameters, handler):
        self.parameters = parameters
        self.handler = handler
