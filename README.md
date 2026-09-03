# Emulite Examples

[Emulite](https://github.com/retrowave3/emulite) examples

## Setup

Install Emulite:

```console
python -m pip install emulite
```

Download `emulite-example-binaries.zip` from the [latest release](https://github.com/retrowave3/emulite-examples/releases/latest) and extract it into the repository root. The archive creates `android/binaries/` and `ios/binaries/`.

## Examples

Run any example directly from the repository root.

### Android

- [`android/jnihandler.py`](android/jnihandler.py): `python android/jnihandler.py`
- [`android/reddit.py`](android/reddit.py): `python android/reddit.py`
- [`android/telegram.py`](android/telegram.py): `python android/telegram.py`
- [`android/tiktok.py`](android/tiktok.py): `python android/tiktok.py`

### iOS

- [`ios/bangbang.py`](ios/bangbang.py): `python ios/bangbang.py`
- [`ios/dewu.py`](ios/dewu.py): `python ios/dewu.py`
- [`ios/ijiami.py`](ios/ijiami.py): `python ios/ijiami.py`
- [`ios/kuaishou.py`](ios/kuaishou.py): `python ios/kuaishou.py`
- [`ios/shopee.py`](ios/shopee.py): `python ios/shopee.py`
- [`ios/sichuanair.py`](ios/sichuanair.py): `python ios/sichuanair.py`
- [`ios/taobao.py`](ios/taobao.py): `python ios/taobao.py`
- [`ios/wtoken.py`](ios/wtoken.py): `python ios/wtoken.py`
- [`ios/xhs.py`](ios/xhs.py): `python ios/xhs.py`
- [`ios/zhihu.py`](ios/zhihu.py): `python ios/zhihu.py`

Each script loads its matching files from the adjacent `binaries/` directory. Emulite uses its installed Android or iOS virtual filesystem by default.
