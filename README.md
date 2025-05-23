<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

# APNEWS-CRAWLER

<em>Unleash the power of real-time news insights.</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/SonPhatTranDeveloper/APNews-Crawler?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/SonPhatTranDeveloper/APNews-Crawler?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/SonPhatTranDeveloper/APNews-Crawler?style=default&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/SonPhatTranDeveloper/APNews-Crawler?style=default&color=0080ff" alt="repo-language-count">

<!-- default option, no dependency badges. -->


<!-- default option, no dependency badges. -->

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
- [Roadmap](#roadmap)

---

## Overview

**Why APNews-Crawler?**

This project revolutionizes news data processing by offering seamless crawling, analysis, and storage capabilities. The core features include:

- **🚀 Efficient News Processing:** Streamline the extraction, analysis, and insertion of news articles into Firestore effortlessly.
- **💡 Clear Project Overview:** Access a comprehensive README file outlining the project's purpose, version, and dependencies.
- **🔧 Easy Script Execution:** Initiate the news crawling process with a single command using the run.sh shell script.

---

## Features

|      | Component       | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Follows a modular design with separate components for data retrieval, processing, and storage.</li><li>Utilizes asynchronous programming with uv.lock for efficient web scraping.</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Consistent coding style and naming conventions throughout the codebase.</li><li>Includes unit tests for critical functions and error handling.</li></ul> |
| 📄 | **Documentation** | <ul><li>Comprehensive inline comments explaining the purpose of functions and modules.</li><li>Lacks external documentation or README files for setup and usage.</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Integrates with external libraries like requests for HTTP requests and dotenv for environment variable management.</li><li>Uses shell scripts for automation and deployment.</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Codebase is divided into reusable modules for specific tasks like crawling, parsing, and storing data.</li><li>Each module has clear responsibilities and interfaces.</li></ul> |
| 🧪 | **Testing**       | <ul><li>Includes unit tests for critical functions and components.</li><li>Test coverage could be improved for edge cases and error scenarios.</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Efficient use of asynchronous programming for concurrent data retrieval.</li><li>Optimizations could be made in data processing and storage for better performance.</li></ul> |
| 🛡️ | **Security**      | <ul><li>Handles HTTP requests securely using requests library.</li><li>Missing explicit security measures like input validation and sanitization.</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Relies on python, uv.lock, pyproject.toml for project setup and execution.</li><li>Dependencies are managed using a lock file (uv.lock) for version consistency.</li></ul> |

---

## Project Structure

```sh
└── APNews-Crawler/
    ├── README.md
    ├── main.py
    ├── pyproject.toml
    ├── run.sh
    ├── src
    │   ├── crawler
    │   │   └── __init__.py
    │   ├── firebase
    │   │   └── __init__.py
    │   ├── llm
    │   │   └── __init__.py
    │   ├── model
    │   │   └── __init__.py
    │   ├── news
    │   │   └── __init__.py
    │   └── utils
    │       └── __init__.py
    └── uv.lock
```

### Project Index

<details open>
	<summary><b><code>APNEWS-CRAWLER/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/SonPhatTranDeveloper/APNews-Crawler/blob/master/pyproject.toml'>pyproject.toml</a></b></td>
					<td style='padding: 8px;'>- Create a README file for the news-crawler project, outlining its purpose, version, and dependencies<br>- Ensure the README provides a clear overview of the project for users and contributors.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/SonPhatTranDeveloper/APNews-Crawler/blob/master/run.sh'>run.sh</a></b></td>
					<td style='padding: 8px;'>- Execute the main Python script for the news crawler project using the provided shell script<br>- This script serves as an entry point to initiate the news crawling process within the project architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/SonPhatTranDeveloper/APNews-Crawler/blob/master/main.py'>main.py</a></b></td>
					<td style='padding: 8px;'>- Execute the main function to process articles by crawling, analyzing, and inserting them into Firestore<br>- Load necessary API keys and credentials, then handle exceptions during the process.</td>
				</tr>
			</table>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** uv

### Installation

Before running, make sure you have the following environment variables set:

```bash
export NEWS_API_KEY=your_newsapi_key
export OPENAI_API_KEY=your_openai_key
export SCRAPER_API_KEY=your_scraperapi_key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account.json
```

You can use a `.env` file and `python-dotenv` to load them automatically in development.

You should also add your custom configuration in `constants.py` file

```python
FIREBASE_PROJECT_ID = "english-news-article"
FIREBASE_COLLECTION = "articles"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TEMP = 0.7
NEWS_SOURCE = "associated-press"
```

Build APNews-Crawler from the source and install dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/SonPhatTranDeveloper/APNews-Crawler
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd APNews-Crawler
    ```

3. **Install the dependencies:**

    ```sh
    ❯ uv pip install -r pyproject.toml
    ```

### Usage

Run the project with:

   ```sh
   ❯ uv python main.py
   ```

---

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square
