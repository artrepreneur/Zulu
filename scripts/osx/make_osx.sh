#!/usr/bin/env bash

# Adapted from https://github.com/spesmilo/electrum/blob/master/contrib/build_tools_util.sh
# SPDX-License-Identifier: MIT

# Parameterize
PYTHON_VERSION=3.7.6

. "$PKT_OSX_PATH/base.sh"

cd "$PKT_OSX_PATH/../.." || fail "failed cd"
ROOT_FOLDER="$(pwd)"
BUILDDIR=${ROOT_FOLDER}/build

command -v brew > /dev/null 2>&1 || fail "Need https://brew.sh/"
command -v xcodebuild > /dev/null 2>&1 || fail "Please install Xcode and xcode command line tools to continue"
command -v git >/dev/null 2>&1 || fail "Need git"

rm -rf "$ROOT_FOLDER/dist"
rm -rf "$BUILDDIR"
chmod 755 "$ROOT_FOLDER/bin/"* || fail "Failed Chmod"
mkdir -p "$BUILDDIR/deps"
VERSION=$(git describe --tags --dirty --always)

# Code Signing: See https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Procedures/Procedures.html
APP_SIGN="Developer ID Application: Healthmatica, Inc (HN2HJ553YW)"
info "Installing Python $PYTHON_VERSION"
export PATH="${HOME}/.pyenv/bin:${HOME}/.pyenv/shims:${HOME}/Library/Python/3.7/bin:$PATH"
if [ -d "${HOME}/.pyenv" ]; then
  pyenv update
else
  curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash > /dev/null 2>&1
fi
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install -s $PYTHON_VERSION && \
pyenv global $PYTHON_VERSION || \
fail "Unable to use Python $PYTHON_VERSION"

info "Installing requirements..."
python3 -m pip install --no-dependencies -Ir ./scripts/deterministic-build/requirements.txt --user || \
fail "Could not install requirements"

info "Installing pyinstaller..."
python3 -m pip install pyinstaller --user || \
fail "Could not install pyinstaller"


if ! [ -f "$BUILDDIR/deps/libzbar.dylib" ]; then
    info "Downloading zbar..."
    curl -L https://homebrew.bintray.com/bottles/zbar-0.10_10.catalina.bottle.tar.gz | \
        tar xz --directory "$BUILDDIR/deps"
    echo "765bd27d0701f71a0e1be28f14c0de1f5b3a9cdcad02a29d22173f21c9ad3df7  $BUILDDIR/deps/zbar/0.10_10/lib/libzbar.0.dylib" | \
        shasum -a 256 -c || fail "zbar checksum mismatched"
    cp "$BUILDDIR/deps/zbar/0.10_10/lib/libzbar.0.dylib" "$BUILDDIR/deps/libzbar.dylib"
fi

if ! [ -f "$BUILDDIR/deps/jpeg/9d/lib/libjpeg.9.dylib" ]; then
    info "Downloading libjpeg..."
    curl -L https://homebrew.bintray.com/bottles/jpeg-9d.catalina.bottle.tar.gz | \
        tar xz --directory "$BUILDDIR/deps"
    echo "f8024b4cbb63121943cba63879ef6075b2dafbb055808f885180686625cd49ef  $BUILDDIR/deps/jpeg/9d/lib/libjpeg.9.dylib" | \
        shasum -a 256 -c || fail "libjpeg checksum mismatched"
fi

info "Building binary"
APP_SIGN="$APP_SIGN" pyinstaller --noconfirm --ascii --clean --name "$VERSION" PKTWallet.spec || \
    fail "Could not build binary"

info "Code signing PKTWallet.app"
codesign --force --options runtime --deep --verify --verbose --entitlements "./scripts/deterministic-build/entitlements.plist" --sign "$APP_SIGN" "dist/PKTWallet.app"

# Notarize the app.
info "Notarizing PKTWallet.app"
ditto -c -k --rsrc --keepParent dist/PKTWallet.app dist/PKTWallet.app.zip
UUID=$(xcrun altool --notarize-app -t osx -f dist/PKTWallet.app.zip --primary-bundle-id PKTWallet -u $APPLE_UNAME -p $APPLE_APP_PWD 2>&1 | awk '/RequestUUID/ { print $NF; }')
info $UUID

request_status="in progress"
while [[ "$request_status" == "in progress" ]]; do
    echo -n "waiting... "
    sleep 10
    request_status=$(xcrun altool --notarization-info $UUID -u $APPLE_UNAME -p $APPLE_APP_PWD 2>&1 | awk -F ': ' '/Status:/ { print $2; }') 
    echo "$request_status"
done
if [[ $request_status != "success" ]]; then
        echo "## could not notarize dist/PKTWallet.app"
        exit 1
fi
ditto -V -x -k --sequesterRsrc --rsrc dist/PKTWallet.app.zip dist
xcrun stapler staple dist/PKTWallet.app
spctl -a -v --type execute dist/PKTWallet.app

info "Installing NODE"
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.35.3/install.sh | bash > /dev/null 2>&1
source ~/.nvm/nvm.sh
nvm install node
nvm use node
node --version

info "Installing appdmg"
npm install -g appdmg --unsafe-perm || \
    fail "Could not install appdmg"

info "Creating PKTWallet.json"
echo -e '{\n\t"title": "pktwallet-'$VERSION'",\n\t"icon": "img/drive.icns",\n\t"contents": [\n\t\t{ "x": 448, "y": 344, "type": "link", "path": "/Applications" },\n\t\t{ "x": 192, "y": 344, "type": "file", "path": "./dist/PKTWallet.app" }\n\t]\n}' > PKTWallet.json || \
    fail "Could not create PKTWallet.json"

info "Creating .DMG"
DMGFILE="pktwallet-"$VERSION".dmg"
appdmg PKTWallet.json dist/$DMGFILE || \
    fail "Could not create .DMG"

#hdiutil create -fs HFS+ -volname PKTWallet -srcfolder dist/PKTWallet.app "dist/pktwallet-$VERSION.dmg" || \
#    fail "Could not create .DMG"

info "Code signing dist/pktwallet-${VERSION}.dmg"
codesign --deep --force --verbose --sign $APP_SIGN "dist/pktwallet-${VERSION}.dmg"
#codesign --force --options runtime --deep --verify --verbose --entitlements "./scripts/deterministic-build/entitlements.plist" --sign $APP_SIGN "dist/pktwallet-${VERSION}.dmg"

if [ -z "$APP_SIGN" ]; then
    warn "App was built successfully but was not code signed. Users may get security warnings from macOS."
    warn "Specify a valid code signing identity as the first argument to this script to enable code signing."
fi
