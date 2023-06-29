# List of DFIR service providers

This is a list of Digital Forensics & Incident Response (DFIR) companies in Finland. These companies can help you in case of a security incident. Purpose of this list is to give organizations a list of active DFIR companies.

## Contributions welcome

1. Fork this repo and then clone the forked repo.

2. Create new branch and set upstream to to this repo, example:

```
git checkout -b add_accenture
git remote add upstream https://github.com/dfir-fi/dfir-fi
```

3. Add new DFIR provider, example:
```
hugo new content/providers/accenture.md
```

4. Add company name and website to the created MD file, example:
```
title: (leave it as it was)
date: (leave it as it was)
draft: (leave it as it was)
company: "Accenture"
website: "https://accenture.com"
```

5. Do commit, example:
```
git add content/providers/accenture.md
git commit -S -m "Added Accenture"
git push -u origin add_accenture
```

6. Create PR on the GitHub page of [this repo](https://github.com/dfir-fi/dfir-fi) by clicking Compare & pull request.
