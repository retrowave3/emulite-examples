import logging
from pathlib import Path

from emulite import IOSApplication

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

binary = Path(__file__).with_name("binaries") / "com.taobao.taobao4iphone" / "Taobao4iPhone"
application = IOSApplication.load(binary.parent, system_runtime=True, allow_incomplete_objc_metadata=True, resolve_dependencies=False)
objc = application.objc
security = objc.require_class("TBSDKSecurity")

with objc.autorelease_pool():
    instance = security.call_method("instance")
    result = instance.call_method(
        "factorSign:input:extendParas:isUseWua:api:requestId:",
        objc.string("21380790"),
        objc.string("&"),
        objc.dictionary({}),
        0,
        objc.string("mtop.taobao.miniapp.top.get"),
        objc.string(""),
    )
    print(f"Sign result: {objc.describe(result)}")

application.close()
