---
title: "Contributions welcome"
layout: "single"
---

## List of DFIR providers   

1. [Fork the source repo](https://github.com/dfir-fi/dfir-fi) and then clone the forked repo.
```
gh repo fork https://github.com/dfir-fi/dfir-fi --clone
```

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

6. Create PR on the GitHub page of [the source repo](https://github.com/dfir-fi/dfir-fi) by clicking Compare & pull request.

## Blog posts and advertising your trainings

Would you be interested in producing technical content for this site that could benefit others interested in the DFIR? Or would you like to advertise your DFIR related training

The blog content produced will be non-commercial and will be produced at your own interest and pace. Content producers will be given their own face and description under the [About](/about) section. If you are interested, please contact [Juho](/about/whois).

The training you advertise can be commercial or freely available to all. If you would like to publish a post about your [training on the site](/training), please contact [Juho](/about/whois).