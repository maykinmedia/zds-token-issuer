from django.conf import settings

from zds_client import ClientAuth


zrc_auth = ClientAuth(
    client_id=settings.ZRC_JWT_CLIENT_ID,
    secret=settings.ZRC_JWT_SECRET,
    scopes=[],
    zaaktypes=[]
)

drc_auth = ClientAuth(
    client_id=settings.DRC_JWT_CLIENT_ID,
    secret=settings.DRC_JWT_SECRET,
    scopes=[],
    zaaktypes=[]
)

ztc_auth = ClientAuth(
    client_id=settings.ZTC_JWT_CLIENT_ID,
    secret=settings.ZTC_JWT_SECRET,
    scopes=['zds.scopes.zaaktypes.lezen']
)

brc_auth = ClientAuth(
    client_id=settings.BRC_JWT_CLIENT_ID,
    secret=settings.BRC_JWT_SECRET,
    scopes=[],
    zaaktypes=[]
)

orc_auth = ClientAuth(
    client_id=settings.ORC_JWT_CLIENT_ID,
    secret=settings.ORC_JWT_SECRET,
    scopes=[],
    zaaktypes=[]
)
