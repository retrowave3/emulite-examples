from __future__ import annotations

import logging
from pathlib import Path

from emulite import AndroidEmulator32, AndroidEmulator64, AndroidEmulatorBase, AndroidProfile, CallEvent, TraceAction

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def setup_arm64() -> AndroidEmulator64:
    emu = AndroidEmulator64(profile=AndroidProfile(package_name="com.reddit.frontpage"))
    module = emu.load_library(Path(__file__).with_name("binaries") / "arm64" / "libreddit-ndk.so")
    module.call_jni_onload()
    return emu


def setup_arm32() -> AndroidEmulator32:
    emu = AndroidEmulator32(profile=AndroidProfile(package_name="com.reddit.frontpage"))
    module = emu.load_library(Path(__file__).with_name("binaries") / "arm32" / "libreddit-ndk.so")
    module.call_jni_onload()
    return emu


def on_call(_emu: AndroidEmulatorBase, event: CallEvent) -> TraceAction:
    print(event.format())
    return TraceAction.CONTINUE


def decrypt_key(emu: AndroidEmulatorBase) -> object:
    trace = emu.call_trace(on_call, module_name="libreddit-ndk.so")
    result = emu.java_class("com.reddit.media.common.apikeys.KeyUtil").call_static("decryptGiphyApiKey", "()Ljava/lang/String;")
    trace.unhook()
    return result


emu32 = setup_arm32()
emu64 = setup_arm64()
key32 = decrypt_key(emu32)
key64 = decrypt_key(emu64)
print(f"giphy key arm32: {key32}")
print(f"giphy key arm64: {key64}")
emu32.close()
emu64.close()
