import logging
from pathlib import Path

from emulite import IOSEmulator64, IOSProfile

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def skip_performance_report(_emulator: IOSEmulator64) -> None:
    logging.getLogger().warning("Kuaishou example skipped the app performance report")


binary = Path(__file__).with_name("binaries") / "com.jiangjia.gif" / "gifCommonFramework"
profile = IOSProfile.from_info_plist(binary.with_name("Info.plist"), code_signature_path=binary)
emulator = IOSEmulator64(profile=profile, system_runtime=True, allow_incomplete_objc_metadata=True)
emulator.load_framework(binary.parent, resolve_dependencies=False)
objc = emulator.objc
guard_manager = objc.require_class("KWOpenSecurityGuardManager")
guard_context = objc.require_class("KWOpenSecurityGuardParamContext")
signature_component = objc.require_class("KWOpenSecureSignatureComponent")
report_hook = objc.add_interceptor("-[KSecurityPerfReport sgPerfReport:message:errorCode:]", skip_performance_report)

with objc.autorelease_pool():
    manager = guard_manager.call_method("getInstance")
    manager.call_method("initSDK")
    manager.call_method("setIsInitialize:", 1)

    allocated_component = signature_component.call_method("alloc")
    component = allocated_component.call_method("init")
    context = guard_context.call_method(
        "createParamContextWithAppKey:paramDict:requestType:input:wbindexKey:bInnerInvoke:sdkid:sdkName:ztconfigFilePath:",
        objc.string("d7b7d042-d4f2-4012-be60-d97ff2429c17"),
        0,
        1,
        objc.data(b"test"),
        objc.string("lD6We1E8i"),
        0,
        objc.string(""),
        objc.string(""),
        objc.string(""),
    )
    component.call_method("atlasSignPlus:", context)
    output = context.call_method("output")
    print(f"Signature: {objc.read_data(output).decode('ascii')}")

report_hook.unhook()
emulator.close()
