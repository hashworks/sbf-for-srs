# SBF(Simple back- and frontend) for SRS

SBF provides a simple configuration, authentication backend server and frontend for [SRS](https://github.com/ossrs/srs).

## Installation

SRSv3, nginx, python, pip and NPM need to be installed on the system.

The AUR provides a [PKGBUILD for Arch Linux](https://aur.archlinux.org/packages/srs): `yay -Syu srs`

```bash
mkdir -p /usr/local/src
cd /usr/local/src
git clone https://github.com/hashworks/sbf-for-srs.git
cd sbf-for-srs

cp srs{,-backend-server}.service /etc/systemd/system

mkdir -p /etc/srs
cp srs{,-backend-server}.conf /etc/srs

cp nginx_vhosts.conf /etc/nginx/sites-available/stream.example.net.conf

cd srs-frontend
npm install

cd ../srs-backend-server
pip install -r requirements.txt
```

Adjust `/etc/srs/srs-backend-server.conf` and `/etc/nginx/sites-available/stream.example.net.conf` according to your liking.

## Components

### Frontend

`srs-frontend` is a HTML5 web-frontend with an MPEG-TS player and a stream key that is adjustable by the URL fragment/hash (f.e. `https://stream.example.net#customkey`, defaults to `public`).

It also provides the direct link to the user (`https://stream.example.net/live/customkey.flv`).

![frontend_with_custom_key](.images/frontend_with_custom_key.png)

### Authentication Backend Server

`srs-backend-server` provides a backend server for SRS that answers the `on-publish` http hook and accepts or denies streams using a provided subnet mask or a list of possible tokens, which can be provided by adding `?token=password` in OBS.

Please note that a VPN network and a subnet mask check should be preferred over tokens since RTMP is unencrypted.

### SRS configuration

`srs.conf` shows an exemplary SRS config. It hosts the frontend in `/usr/local/src/sbf/srs-frontend` on port `57643` and RTMP on its default `1935` and talks to the `srs-backend-server` on `http://127.0.0.1:59354`. It is configured for low latency (2-3s).

`nginx_vhost.conf` shows how to configure a nginx vHost towards SRS.

![obs setting with public key](.images/public_key_with_allowed_ip.png)

![obs setting with custom key and token](.images/custom_key_with_allowed_token.png)