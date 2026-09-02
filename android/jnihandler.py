from __future__ import annotations

import logging
from pathlib import Path

from emulite import AndroidEmulator64, JniHandler

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


class DemoJniHandler(JniHandler):
    def call_static_method(self, method, args):
        target = f"{method.java_class.name}.{method.name}{method.signature}"
        if target == "com/github/unidbg/android/JniTest.nestedRun(Ljava/lang/String;JID)J":
            text, long_arg, int_arg, double_arg = args
            print(f"  native -> Java  nestedRun({text.value!r}, {long_arg}, {int_arg}, {double_arg})")
            return 0x1122334455667788
        return super().call_static_method(method, args)


emu = AndroidEmulator64(jni_handler=DemoJniHandler())
emu.load_library(Path(__file__).with_name("binaries") / "arm64" / "libnative.so")
native = emu.java_class("com.github.unidbg.android.JniTest")
print("calling native testJni(...)")
native.call_static(
    "testJni", "(Ljava/lang/String;JIDZSFDBJF)V", "hello from python", 0x123456789ABCDEF, 0x789A, 0.12345, True, 0x123, 0.456, 0.789, 0x7F, 0x89ABCDEF, 0.123
)
print("done")
emu.close()
