from blacksheep.messages import Request, Response
from blacksheep.server.bindings import ServerInfo
from blacksheep.server.routing import Route, Router
from blacksheep.server.responses import redirect, text, json, html,bad_request
from modules.ip_todo import _ip
from modules.qq_todo import _qq
from modules.yiyan_todo import _yiyan
from modules.randimg_todo import randimg
from dataclass import Get_ua_result,Ip_result,Qq_info,randimg_result
router = Router()
get = router.get
add_get = router.add_get

@get("/ip")
async def Get_ip(ipinfo: _ip, ip: str) -> Ip_result|Response:
    try:
        return await ipinfo.GetIp(ip)
    except Exception as e:
        return bad_request(e.__str__())

@get("/ua")
async def Get_ua(request: Request,ip:ServerInfo,ipinfo: _ip) -> Get_ua_result|Response:
    header = dict([(bytes.decode(i),bytes.decode(j)) for i,j in request.headers])
    ip = header['x-real-ip'] if "x-real-ip" in header.keys() else ip.value[0]
    try:
        _ipinfo = await ipinfo.GetIp(ip)
    except Exception as e:
        return bad_request(e.__str__())
    return Get_ua_result(ip,header,_ipinfo.data)

Route.value_patterns["qq"] = r"[0-9]{5,10}"

@get("/qq/{qq:qqnum}")
async def Get_Qq(qqnum:int,Qqinfo: _qq) -> Qq_info|Response:
    try:
        return await Qqinfo.Get_qqinfo(qqnum)
    except Exception as e:
        return bad_request(e.__str__())

@get("/randimg")
async def Randimg(request: Request,rdimg:randimg,encode:str = None,n: int = 1,type:str = 'pc') -> Response|randimg_result:
    ua = request.get_first_header(b'user-agent')
    try:
        assert (ua is not None and encode in ['json',None] and type in ['pc','mobile']),'请检查参数'
        assert (n <= 10),'请求数量超过上限'
        ua = bytes.decode(ua)
        _format = '!q80.webp' if rdimg.check_Version(ua) else '!q80.jpeg'
        match [encode,type]:
            case [None,'pc']:
                return redirect(rdimg.pc() + _format)
            case [None,'moblie']:
                return redirect(rdimg.mb() + _format)
            case ['json','pc']:
                return randimg_result(200,rdimg.more_pc(n,_format))
            case ['json','mobile']:
                return randimg_result(200,rdimg.more_mb(n,_format))
    except Exception as e:
        return bad_request(randimg_result(400,e.__str__()))
    
@get('/yiyan')
async def yiyan(request: Request,yy:_yiyan,c:str = None,encode: str = None) -> Response:
    try:
        assert c is not None
        t = request.query.get('c')
        slist = [x for x in t if x in yy.type_list]
        assert slist is not []
        result = yy.cut_get_yiyan(slist)
    except:
        result = yy.get_yiyan()
    if encode == 'text':
        return html(str(result))
    else:
        return json(result)