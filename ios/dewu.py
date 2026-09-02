import logging
import sys
from io import TextIOWrapper
from pathlib import Path

from emulite import IOSApplication, IOSEmulator64
from emulite.ios.abi import DarwinSecurityStatus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
if isinstance(sys.stdout, TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")


def return_empty_keychain(emulator: IOSEmulator64) -> int:
    output = emulator.get_argument_pointer(1)
    if output:
        output.write_pointer(0)
    logging.getLogger().warning("Dewu keychain lookup reported no matching item")
    return DarwinSecurityStatus.SUCCESS


binary = Path(__file__).with_name("binaries") / "com.siwuai.duapp" / "5.61.4" / "DUApp"
application = IOSApplication.load(
    binary.parent, system_runtime=True, allow_incomplete_objc_metadata=True, resolve_dependencies=False, run_objc_load_methods=False, run_initializers=False
)
emulator = application.emulator
module = application.module
keychain_hook = emulator.intercept("_SecItemCopyMatching", return_empty_keychain)
module.call_offset(0x99FF380)
objc = application.objc
du_sanwa_sdk = objc.require_class("DuSanwaSDK")

with objc.autorelease_pool():
    headers = objc.dictionary({"sks": "2,1,0", "Content-Type": "application/json;charset=UTF-8"})
    response = objc.data(Path(__file__).with_name("dewu_response.json").read_bytes().rstrip(b"\r\n"))
    request_path = objc.string("/api/v1/app/index/ice/flow/product/detailV5")
    result = du_sanwa_sdk.call_method("duSecDouDecodeWithHeader:origionData:path:", headers, response, request_path)
    print(f"Decrypted: {objc.read_data(result).decode('utf-8')}")

keychain_hook.unhook()
application.close()
