import json
import logging
from pathlib import Path

from emulite import IOSApplication, IOSEmulator64, IOSProfile, ReplacementAction
from emulite.ios.abi import DarwinSecurityStatus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def return_empty_keychain(emulator: IOSEmulator64) -> ReplacementAction:
    output = emulator.get_argument_pointer(1)
    if output:
        output.write_pointer(0)
    logging.getLogger().warning("BangBang keychain lookup reported no matching item")
    emulator.set_return_value(DarwinSecurityStatus.ITEM_NOT_FOUND)
    return ReplacementAction.SKIP_ORIGINAL


def reject_keychain_add(emulator: IOSEmulator64) -> ReplacementAction:
    output = emulator.get_argument_pointer(1)
    if output:
        output.write_pointer(0)
    logging.getLogger().warning("BangBang keychain write rejected because persistence is unavailable")
    emulator.set_return_value(DarwinSecurityStatus.NOT_AVAILABLE)
    return ReplacementAction.SKIP_ORIGINAL


binary = Path(__file__).with_name("binaries") / "com.ceair.b2m" / "ceair_iOS_branch"
profile = IOSProfile.from_info_plist(binary.with_name("Info.plist"), bundle_id="com.ceair.b2m", executable_name=binary.name, code_signature_path=binary)
profile.bundle_path = f"{profile.bundle_container_path}/com.ceair.b2m"
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
module = application.module
keychain_hook = module.hook_import("_SecItemCopyMatching", return_empty_keychain)
keychain_add_hook = module.hook_import("_SecItemAdd", reject_keychain_add)
objc = application.objc

with objc.autorelease_pool():
    objc.require_class("Sciapodous").call_method("load")
    for entry in module.init_functions():
        if module.offset_of(entry) not in {0x2FF3B20, 0x2FF414C, 0x2FF4320}:
            emulator.call(entry)

    bang_safe_sdk = objc.require_class("BangSafeSDK")
    payload = {"osVersion": emulator.device.product_version, "os": "iOS", "deviceModel": emulator.device.hardware_machine, "channelNo": "APPSTORE"}
    input_value = objc.string("S" + json.dumps(payload, separators=(",", ":")))
    result = bang_safe_sdk.call_method("checkcode:dataStyle:", input_value, 2)
    print(f"Encrypted: {objc.read_string(result)}")

keychain_add_hook.unhook()
keychain_hook.unhook()
application.close()
