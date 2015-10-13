#!/bin/sh

cd ..
curl -O http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.9/sip-4.16.9.tar.gz/download
tar -xvf sip-4.16.9.tar.gz
cd sip-4.16.9
python configure.py
make
sudo make install
cd ..
curl -O http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz/download
tar -xvf PyQt-x11-gpl-4.11.4.tar.gz
cd PyQt-x11-gpl-4.11.4
python configure.py --confirm-license
make
sudo make install
cd ../swan
