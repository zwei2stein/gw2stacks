rm -rf ./build
rm -r ./dist
rm ./*.spec
ver=$(cut -d "'" -f2 < version.py)
nicegui-pack --onefile --name "GW2 inventory cleanup tool"$ver app.py