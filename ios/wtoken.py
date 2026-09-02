import logging
from pathlib import Path

from emulite import IOSApplication, IOSEmulator64, NativePointer
from emulite.ios.abi import DarwinSecurityStatus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def initialize_without_cellular_service(emulator: IOSEmulator64) -> NativePointer:
    logging.getLogger().warning("WToken example initialized without cellular service")
    return emulator.get_argument_pointer(0)


def return_empty_keychain(emulator: IOSEmulator64) -> int:
    output = emulator.get_argument_pointer(1)
    if output:
        output.write_pointer(0)
    logging.getLogger().warning("WToken keychain lookup returned empty data")
    return DarwinSecurityStatus.SUCCESS


binary = Path(__file__).with_name("binaries") / "com.csair.MBP" / "CSMBP-AppStore-Package"
application = IOSApplication.load(
    binary.parent, system_runtime=True, allow_incomplete_objc_metadata=True, resolve_dependencies=False, run_objc_load_methods=False, run_initializers=False
)
emulator = application.emulator
objc = application.objc
tally_class = objc.require_class("AliTigerTally")
network_info_hook = objc.add_interceptor("-[CTTelephonyNetworkInfo init]", initialize_without_cellular_service)
keychain_hook = emulator.intercept("_SecItemCopyMatching", return_empty_keychain)

with objc.autorelease_pool():
    tally = tally_class.call_method("sharedInstance")
    tally.call_method(
        "initialize:",
        objc.string(
            "xPEj7uv0KuziQnXUyPIBNUjnDvvHuW09VOYFuLYBcY-jV6fgqmfy5B1y75_iSuRM5U2zNq7MRoR9N1F-UthTEgv-QBWk68gr95BrAySzWuDzt08FrkeBZWQCGyZ0iAybalYLOJEF7nkKBtmDGLewcw=="
        ),
    )
    result = tally.call_method("vmpSign:", objc.data(b'{"biClassId":["2","3","4"]}'))
    print(f"Sign result: {objc.read_string(result)}")

keychain_hook.unhook()
network_info_hook.unhook()
application.close()
