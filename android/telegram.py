from __future__ import annotations

import logging
from pathlib import Path

from emulite import AndroidEmulator32, AndroidEmulator64, AndroidEmulatorBase, AndroidProfile, ReplacementAction

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def setup_arm64() -> AndroidEmulator64:
    emu = AndroidEmulator64(profile=AndroidProfile(package_name="org.telegram.messenger"))
    module = emu.load_library(Path(__file__).with_name("binaries") / "arm64" / "libtmessages.49.so")
    module.call_jni_onload()
    return emu


def setup_arm32() -> AndroidEmulator32:
    emu = AndroidEmulator32(profile=AndroidProfile(package_name="org.telegram.messenger"))
    module = emu.load_library(Path(__file__).with_name("binaries") / "arm32" / "libtmessages.49.so")
    module.call_jni_onload()
    return emu


def run_crypto(emu: AndroidEmulatorBase) -> tuple[str, str]:
    pending_sizes: list[int] = []
    allocations: list[tuple[int, int]] = []

    def before_malloc(hooked_emu: AndroidEmulatorBase) -> ReplacementAction:
        pending_sizes.append(hooked_emu.get_argument(0))
        return ReplacementAction.CALL_ORIGINAL

    def after_malloc(hooked_emu: AndroidEmulatorBase) -> None:
        allocations.append((pending_sizes.pop(), hooked_emu.get_return_value()))

    utils = emu.java_class("org/telegram/messenger/Utilities")
    module = emu.require_module("libtmessages.49.so")
    malloc_hook = module.hook_import("malloc", before_malloc, after_malloc)
    password, salt, dst = bytearray(b"123456"), bytearray(8), bytearray(64)
    utils.call_static("pbkdf2", "([B[B[BI)V", password, salt, dst, 256)

    data, key, iv = bytearray(16), bytearray(32), bytearray(16)
    utils.call_static("aesCtrDecryptionByteArray", "([B[B[BIIJ)V", data, key, iv, 0, 16, 0)
    malloc_hook.unhook()

    arch = f"arm{emu.arch.pointer_size * 8}"
    print(f"{arch} malloc calls: " + ", ".join(f"{size} bytes -> {address:#x}" for size, address in allocations))
    return dst.hex(), data.hex()


emu32 = setup_arm32()
emu64 = setup_arm64()
pbkdf2_32, aes_ctr_32 = run_crypto(emu32)
pbkdf2_64, aes_ctr_64 = run_crypto(emu64)
print(f"arm32 pbkdf2 : {pbkdf2_32}")
print(f"arm32 aes-ctr: {aes_ctr_32}")
print(f"arm64 pbkdf2 : {pbkdf2_64}")
print(f"arm64 aes-ctr: {aes_ctr_64}")
emu32.close()
emu64.close()
