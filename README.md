# Snek
![snek's github banner](https://raw.githubusercontent.com/matteocargnelutti/snek/master/misc/snek-banner-tmp-1750x.png "snek")

**A simple and minimalistic static-site generator for Python.**

**Current version:** v0.1.0 - _"Danger noodle"_

---

## Summary
- [Concept](#concept)
- [Getting Started](#getting-started)
- [Folders structure](#folders-structure)
- [Configuration](#configuration)
- [Content management](#content-management)
- [Shared data](#shared-data)
- [Templating](#templating)
- [Netlify and Netlify CMS](#netlify-and-netlify-cms)
- [API reference ?](#api-reference)
- [Contributing](#contributing)

Follow me on Twitter: [@macargnelutti](https://twitter.com/macargnelutti).

---

## Concept

### Snek is a static site generator / framework that was designed with two ideas in mind:
- It has to be **as simple as possible**, end to end
- It has to work as a **Python module** so it can be integrated in any program

### Its main features are :
- **JSON front-matter + Markdown** content files
- **JSON shared data files** that can be accessed from any template
- Works as a **Python module**, can be integrated and extended easily
- [**Mako**](https://www.makotemplates.org/) templating engine
- Out-of-the box [**SASS**](https://sass-lang.com/) processing
- Compatible with [**Netlify**](https://www.netlify.com/) and [**Netlify CMS**](https://www.netlifycms.org/)
- **Simple structure:** few requirements and interchangeable folders architecture.

I really hope you'll like this very first version of **Snek**. Without further ado: let's get started.

[☝️ Back to summary](#summary)

---

## Getting Started

### Pre-requisites
- An UNIX-like OS _(Linux, MacOS, etc ...)_
- Curl _(Mac users can install it via [brew.sh](https://brew.sh/).)_
- Python 3.7+ recommended
- [pipenv](https://pipenv.kennethreitz.org/en/latest/)

### Installing snek and the project template
**From your empty project's folder, run the following command:**
```bash
curl https://raw.githubusercontent.com/matteocargnelutti/snektools/master/snektools.sh > snektools.sh && chmod a+x snektools.sh && ./snektools.sh
```

This will install the [snektools](https://github.com/matteocargnelutti/snektools), a series of bash scripts that will help you with your **Snek** project, and run `snekinit` that will install a basic project template.

We'll review the project's structure in the [Folders structure](#folders-structure) chapter of this document.

If you'd rather install everything manually, you can install [`snek-framework` from Pypi via pip](https://pypi.org/project/snek-framework/).

### Building
**Snek**'s main mission is to process files to generate HTML pages. The project template installed by `snekinit` contains enough data to do just that, let's give it a try.

`website.py` contains a bit of **minimal bootstrap code** allowing to build the website:

```python
website = Snek()
website.build()
```

To build the current project, simply run `pipenv run python website.py` _(or `python website.py` if you are within your `pipenv` environment)_: this will generate your website in a `build/` folder. 
Inside this folder, you will see an `index.html` file: the **Snek** has done its job and has built the website.

### Serving locally over HTTP
One of the [snektools](https://github.com/matteocargnelutti/snektools), `snekserve`, does two things:
- It builds your website by calling `website.py`
- It serves the content of the `build/` folder over HTTP so you can access it in your browser easily.

**Inside your project folder, simply run:**
```bash
./snekserve.sh
```

**Open your browser, and go to `http://localhost:8081` to see your website:**

<img alt="snekinit screenshot" src="https://raw.githubusercontent.com/matteocargnelutti/snek/master/misc/screenshot-snekinit.png">

`snekserve` contains a very primivite loop that will keep rebuilding your website: every change you make will be accessible shortly after.

**You are now ready to go !**
Let's dive a little bit deeper to see what we can do.

[☝️ Back to summary](#summary)

---

## Folders structure

Once your project is initialized, its structure should look like this.
The folder structure described here can be entierly changed via [SnekConfig](#configuration)

| Folder or file      | Role                                                                                                                       |
|---------------------|----------------------------------------------------------------------------------------------------------------------------|
| `assets/`           | Contains all the static files that the website needs.                                                                      |
| `build/`            | The generated website will live here. Created on the spot if need be.                                                      |
| `content/`          | Contains .json.md _(json front-matter markdown)_ representing content pages. Can contain nested folders.                   |
| `data/`             | Contains .json file used as _"shared data"_ across all templates. Can contain nested folders.                              |
| `js/`               | Contains JavaScript files that the website needs.                                                                          |
| `scss/`             | Contains .scss files to be processed. Processed files will be in a `css` sub-folder of `build/` once the website is built. |
| `css/`              | **Optional.** To be used if scss processing is deactivated. Will contain all the css files the website needs.              |
| `templates/`        | Contains `mako` templates.                                                                                                 |
| `website.py`        | Main entry point. This file will build the website.                                                                        |


[☝️ Back to summary](#summary)

---

## Configuration

**Snek's** can be used out of the box without any configuration, but every parameter can be changed via `SnekConfig` object passed to `Snek`.

### Available options

| Parameter name      | Type | Description                                                                                | Default         |
|---------------------|------|--------------------------------------------------------------------------------------------|-----------------|
| `build_path`        | str  | Path to the project's build destination. Will be created if it does not exists.            | `'./build'`     |
| `content_path`      | str  | Path to the project's content files. Must exist.                                           | `'./content'`   |
| `data_in_build`     | bool | If True, will copy data files to the built websites so they can be accessed via JavScript. | `'False'`       |
| `data_path`         | str  | Path to the project's data files.                                                          | `'./data'`      |
| `templates_path`    | str  | Path to the project's templates files.                                                     | `'./templates'` |
| `js_path`           | str  | Path to the project's JavaScript files.                                                    | `'./js'`        |
| `assets_path`       | str  | Path to the project's assets files.                                                        | `'./assets'`    |
| `css_path`          | str  | Path to the project's CSS files. Ignored if scss_active is True.                           | `'./css'`       |
| `scss_active`       | bool | Determines if files from the SCSS folder should be processed instead of CSS.               | `True`          |
| `scss_path`         | str  | Path to the project's SCSS files.                                                          | `'./scss'`      |
| `scss_output_style` | str  | Can be `'compressed'` , `'nested'` or `'expanded'`.                                        | `'/compressed'` |

### Usage
To replace the default configuration by a custom one, simply create a `SnekConfig` object to be passed to `Snek`.

```python
from snek import Snek, SnekConfig

config = SnekConfig(scss_active=False)
website = Snek(config)
website.build()
```

[☝️ Back to summary](#summary)

---

## Content management

### JSON frontmatter markdown
Files in the **content folder** are expected to use the **JSON frontmatter markdown** format: that means that the file contains first a **JSON object** with meta data, and then some **markdown** content.

```markdown
{
    "title": "Snek Project Template",
    "template": "index.html"
}

## Hello world !
Your basic snek project is ready to go !
```

### Defining a template to use for a given content file
The `template` frontmatter field of a content file defines the template that will be used to render the file.

If none defined, **Snek** will pick the first template available.

The name must match a file present in the templates folder _(`templates/`)_. Having sub-folders of templates work.

### Accessing the sitemap programmatically
When a `Snek` object is created, it parses content to build a sitemap. You can access this sitemap programmatically.

```python
website = Snek()
website.sitemap # dict containing the complete sitemap and all the metadata of every content file.
```

Each entry in the sitemap contains all the meta data of all the files.

```python
website.sitemap['index']['title'] # "Snek Project Template"
```

Editing this dict will have no impact on the built pages: consider it **read-only**.

A **flat** version of the sitemap, containing only the filenames, is also available:

```python
website.sitemap_flat # List of content files
```

[☝️ Back to summary](#summary)

---

## Shared data

☠️ **Work in progress, documentation to come.**

### Concept
The content of the **shared data folder** _(`data/`)_ is parsed and made accessible across the entire website.

This is really usefull to build features that live on multiple pages.

### Accessing and editing shared data programmatically
```python
website = Snek()
website.data # dict containing all the data from the shared data folder
```

As opposed to the sitemap, `Snek.data` can be edited: this means that you can dynamically add data items easily to your website at build time: This is usefull for example to fetch content from an API that you want to display.

[☝️ Back to summary](#summary)

---

## Templating

**Snek** uses the [Mako templating engine](https://www.makotemplates.org/): please have a look at their [great documentation](https://docs.makotemplates.org/en/latest/) for details.

**Each template has access to the following variables:**

| Name       | Type   | Description                                                                      |
|------------|--------|----------------------------------------------------------------------------------|
| `data`     | dict   | Shared data object _(contents from the data folder)_.                            |
| `sitemap`  | dict   | Complete sitemap, allowing to access all the other pages' filename and metadata. |
| `config`   | dict   | dict version of Snek's config.                                                   |
| `metadata` | dict   | Parsed JSON front matter of the content file.                                    |
| `content`  | string | Parsed Markdown (HTML) of the content file.                                      |

### Examples
```html
<!-- Accessing a meta data field of the current page -->
<title>${metadata['title']}</title>
```

```html
<!-- Accessing the content of the current page -->
<div>${content}</div>
```

```html
<!-- Accessing shared data -->
<a href="${data['globals']['github_url']}" title="Snek on GitHub">- More info on GitHub -</a>
```

[☝️ Back to summary](#summary)

---

## Netlify and Netlify CMS

This quick guide will provide details to help setting up **Snek** on [Netlify](https://www.netlify.com/) and [Netlify CMS](https://www.netlifycms.org/),but won't go step-by-step into configuring both. 

Please have a look at their respective documentations if you are not familiar with these technologies.

### Deploy to Netlify

As you are hooking your **GitHub repository containing your Snek website** to **Netlify**, simply use the following build configuration:
- **Build command:** `python website.py` _(change name accordingly if need be)_
- **Publish directory:** `build/` _(change name accordingly if need be)_

That is it ! Your website will automatically deploy, [just like this one](https://snek-netlify-test.netlify.com).

### Netlify CMS setup

If you have followed the [_"Getting Started"_](#getting-started) guide, you probably have a `sneklifycms.sh` file in your folder: executing this file will created an `admin/` folder containing a basic [Netlify CMS](https://www.netlifycms.org/) configuration matching the basic project template.

```bash
./sneklifycms.sh
```

On **Netlify**, simply edit the build command to the following, so `admin/` files are part of the built website:
- **Build command:** `python website.py; mv admin/ build/admin/;` _(change name accordingly if need be)_

You will need to have **Netlify Identity** in **Invite mode** as well as **GitHub Gateway** enabled to be able to connect to **Netlify CMS** _(see documentation)_. 

Once you **invited yourself** as an **Identity user**, make sure the invite url contains `/admin/` to be able to register:
- **From:** `https://[WEBSITE-NAME].netlify.com/#invite_token=[INVITE-TOKEN]`
- **To:** `https://[WEBSITE-NAME].netlify.com/admin/#invite_token=[INVITE-TOKEN]`

You will then be able to edit your website via **Netlify CMS**: 

<img alt="Netlify CMS 1" src="https://raw.githubusercontent.com/matteocargnelutti/snek/master/misc/screenshot-netlify-cms-2.png">

[☝️ Back to summary](#summary)

---

## API reference

#### Snek is made of two main files which are extensively commented and purposefuly simple that you can consult here:
- [snekconfig.py](https://github.com/matteocargnelutti/snek/blob/master/snek/snekconfig.py)
- [snek.py](https://github.com/matteocargnelutti/snek/blob/master/snek/snek.py)

[☝️ Back to summary](#summary)

---

## Contributing

**Snek** is in its infancy: if you find bugs, have ideas on how to improve it, or would like to get involved in any other way please feel free to reach out in the [issues](https://github.com/matteocargnelutti/snek/issues).

---
