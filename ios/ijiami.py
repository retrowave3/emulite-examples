import logging
from pathlib import Path

from emulite import IOSApplication, IOSEmulator64

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def pass_environment_check(_emulator: IOSEmulator64) -> int:
    logging.getLogger().warning("Ijiami example bypassed the app environment check")
    return 1


binary = Path(__file__).with_name("binaries") / "com.csair.MBP" / "CSMBP-AppStore-Package"
application = IOSApplication.load(
    binary.parent, system_runtime=True, allow_incomplete_objc_metadata=True, resolve_dependencies=False, run_objc_load_methods=False, run_initializers=False
)
emulator = application.emulator
module = application.module
module.call_address(0x38EAD94)
module.call_address(0x38EFA18)
check_hook = emulator.intercept(module.pointer_at(0x38F0004), pass_environment_check)
objc = application.objc
jm_box = objc.require_class("JMBox125")

with objc.autorelease_pool():
    result = jm_box.call_method("JMBox167:JMBox501:", objc.string('{"biClassId":["2","3","4"]}'), 1)
    print(f"Encrypted: {objc.read_string(result)}")

check_hook.unhook()
application.close()
