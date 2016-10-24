# podir
Podcast Search Engine and Directory

## Install Notes

## Requirements

```
sudo apt-get install zlib1g-dev
sudo apt-get install g++
sudo apt-get install uuid-dev
```

### Xapian

Xapian in python3 virtualenv

```
export VENV=$VIRTUAL_ENV
mkdir $VENV/packages && cd $VENV/packages

export XAP_VER=1.4.1

curl -O http://oligarchy.co.uk/xapian/$XAP_VER/xapian-core-$XAP_VER.tar.xz
curl -O http://oligarchy.co.uk/xapian/$XAP_VER/xapian-bindings-$XAP_VER.tar.xz

tar xvf xapian-core-$XAP_VER.tar.xz
tar xvf xapian-bindings-$XAP_VER.tar.xz

cd $VENV/packages/xapian-core-$XAP_VER
./configure --prefix=$VENV && make && make install

export LD_LIBRARY_PATH=$VENV/lib

cd $VENV/packages/xapian-bindings-$XAP_VER
./configure --prefix=$VENV --with-python3 && make && make install

python -c "import xapian"
```
