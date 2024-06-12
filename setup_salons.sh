cp -rf air-france-media salons
cd salons
rm -rf .git/ app/
rmdir .git app
ln -s ../salons-reno-deco app
