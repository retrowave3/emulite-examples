import logging
from pathlib import Path

from emulite import IOSApplication

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

binary = Path(__file__).with_name("binaries") / "cn.com.scal.sichuanair"
application = IOSApplication.load(binary, system_runtime=True, allow_incomplete_objc_metadata=True, resolve_dependencies=False)
objc = application.objc
zsch_rsa = objc.require_class("ZSCHRSA")

with objc.autorelease_pool():
    result = zsch_rsa.call_method("getReqSign:", objc.string("Mocha"))
    print(f"Request signature: {objc.describe(result)}")

application.close()
