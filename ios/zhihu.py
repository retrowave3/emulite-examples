import logging
from pathlib import Path

from emulite import IOSApplication, IOSProfile

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

binary = Path(__file__).with_name("binaries") / "com.zhihu.ios" / "osee2unifiedRelease"
profile = IOSProfile.from_info_plist(binary.with_name("Info.plist"), seed=0, code_signature_path=binary)
application = IOSApplication.load(
    binary.parent,
    profile=profile,
    system_runtime=True,
    allow_incomplete_objc_metadata=True,
    resolve_dependencies=False,
    run_objc_load_methods=False,
    run_initializers=False,
)
emulator = application.emulator
objc = application.objc
request_class = objc.require_class("NSURLRequest")

with objc.autorelease_pool():
    result = request_class.call_method(
        "encryptWithZse83:path:APPVersion:authorization:UDID:body:signatureVersion:",
        objc.string("101_2_1.0"),
        objc.string("/message-push/event"),
        objc.string("10.26.0"),
        objc.string(""),
        objc.string(emulator.device.udid),
        objc.string('{"report_time":1729768217954,"type":5}'),
        objc.string("1.0"),
    )
    print(f"x-zse-96: {objc.read_string(result)}")

application.close()
