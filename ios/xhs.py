import logging
from pathlib import Path

from emulite import IOSApplication, IOSEmulator64
from emulite.ios.abi import DarwinSecurityStatus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def return_empty_keychain(emulator: IOSEmulator64) -> int:
    output = emulator.get_argument_pointer(1)
    if output:
        output.write_pointer(0)
    logging.getLogger().warning("Xiaohongshu keychain lookup returned empty data")
    return DarwinSecurityStatus.SUCCESS


binary = Path(__file__).with_name("binaries") / "com.xingin.discover" / "8.74" / "discover"
application = IOSApplication.load(
    binary.parent, system_runtime=True, allow_incomplete_objc_metadata=True, resolve_dependencies=False, run_objc_load_methods=False, run_initializers=False
)
emulator = application.emulator
objc = application.objc
options_class = objc.require_class("TIOptions")
tiny_class = objc.require_class("TITiny")
keychain_hook = emulator.intercept("_SecItemCopyMatching", return_empty_keychain)

with objc.autorelease_pool():
    options = options_class.call_method("sharedInstance")
    options.call_method("setAppID:", objc.string("ECFAAF02"))
    tiny_class.call_method("initializeWithOptions:", options)
    result = tiny_class.call_method(
        "signWithMethod:url:payload:", objc.string("GET"), objc.string("https://edith.xiaohongshu.com/api/sns/v1/system_service/config"), 0
    )
    print(f"Sign result: {objc.describe(result)}")

keychain_hook.unhook()
application.close()
