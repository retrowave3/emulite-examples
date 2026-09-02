from __future__ import annotations

import logging
from pathlib import Path

from emulite import AndroidEmulator32, AndroidEmulator64, AndroidEmulatorBase, AndroidProfile, ReplacementAction, TraceAction, TraceInfo

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def setup_arm64() -> AndroidEmulator64:
    emu = AndroidEmulator64(profile=AndroidProfile(package_name="com.zhiliaoapp.musically"))
    module = emu.load_library(Path(__file__).with_name("binaries") / "arm64" / "libEncryptor.so")
    module.call_jni_onload()
    return emu


def setup_arm32() -> AndroidEmulator32:
    emu = AndroidEmulator32(profile=AndroidProfile(package_name="com.zhiliaoapp.musically"))
    module = emu.load_library(Path(__file__).with_name("binaries") / "arm32" / "libEncryptor.so")
    module.call_jni_onload()
    return emu


def on_trace_step(_emu: AndroidEmulatorBase, info: TraceInfo) -> TraceAction:
    print(info.format())
    return TraceAction.CONTINUE


def before_memcpy(emu: AndroidEmulatorBase) -> ReplacementAction:
    dst, src, n = emu.get_argument(0), emu.get_argument(1), emu.get_argument(2)
    print(f"memcpy({dst:#x}, {src:#x}, {n})")
    return ReplacementAction.CALL_ORIGINAL


def before_time(emu: AndroidEmulatorBase) -> ReplacementAction:
    replacement_value = 123456789
    emu.set_return_value(replacement_value)
    print(f"replaced time: {replacement_value}")
    return ReplacementAction.SKIP_ORIGINAL


def encrypt(emu: AndroidEmulatorBase, data: bytes, trace: bool = False) -> bytes:
    memcpy_hook = emu.hook_import("memcpy", before_memcpy)
    time_hook = emu.hook_import("time", before_time)
    trace_hook = emu.trace_code(on_trace_step) if trace else None
    result = emu.call_static_native("com/bytedance/frameworks/encryptor/EncryptorUtil", "ttEncrypt", "([BI)[B", data, len(data))
    if trace_hook is not None:
        trace_hook.unhook()
    time_hook.unhook()
    memcpy_hook.unhook()
    return bytes(result)


emu32 = setup_arm32()
emu64 = setup_arm64()

data = b"hello world"
emu32_result = encrypt(emu32, data, trace=False)
emu64_result = encrypt(emu64, data, trace=False)

print(f"ttencrypt arm32: {bytes(emu32_result).hex()}")
print(f"ttencrypt arm64: {bytes(emu64_result).hex()}")
emu32.close()
emu64.close()
