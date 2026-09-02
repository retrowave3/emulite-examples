import logging
from pathlib import Path

from emulite import IOSApplication, IOSEmulator64
from emulite.ios.abi import DarwinSecurityStatus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def return_zero_mmp_id(_emulator: IOSEmulator64) -> int:
    logging.getLogger().warning("Shopee example replaced getMMPId with zero")
    return 0


def return_empty_keychain(emulator: IOSEmulator64) -> int:
    result_pointer = emulator.get_argument_pointer(1)
    if result_pointer:
        result_pointer.write_u64(0)
    logging.getLogger().warning("Shopee example reported an empty guest keychain")
    return DarwinSecurityStatus.SUCCESS


def skip_application_client_dealloc(_emulator: IOSEmulator64) -> None:
    logging.getLogger().warning("Shopee example skipped UISApplicationSupportClient dealloc assertion")


binary = Path(__file__).with_name("binaries") / "com.beeasy.shopee.sg" / "ShopeeSG"
application = IOSApplication.load(binary.parent, system_runtime=True, allow_incomplete_objc_metadata=True, resolve_dependencies=False, run_initializers=False)
emulator = application.emulator
objc = application.objc
security_sdk_manager = objc.require_class("ShopeeSecuritySDKManager")
mmp_id_hook = objc.add_interceptor("-[SHPSECminiSDKManager getMMPId]", return_zero_mmp_id)
keychain_hook = emulator.intercept("_SecItemCopyMatching", return_empty_keychain)
application_client_hook = objc.add_interceptor("-[UISApplicationSupportClient dealloc]", skip_application_client_dealloc)

with objc.autorelease_pool():
    result = security_sdk_manager.call_method("genSignWithURL:data:", objc.string("https://mall.shopee.sg/api/v4/pages/get_category_tree"), 0)
    print(f"Signature: {objc.describe(result)}")

application_client_hook.unhook()
keychain_hook.unhook()
mmp_id_hook.unhook()
application.close()
