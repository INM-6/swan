#!/bin/sh

cd ..
curl -O "http://downloads.sourceforge.net/project/pyqt/sip/sip-4.16.9/sip-4.16.9.tar.gz"
tar -xvf sip-4.16.9.tar.gz
cd sip-4.16.9
python configure.py
make
sudo make install
cd ..
curl -O "http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz"
tar -xvf PyQt-x11-gpl-4.11.4.tar.gz
cd PyQt-x11-gpl-4.11.4
python configure.py --confirm-license
make
sudo make install
cd ../swan
