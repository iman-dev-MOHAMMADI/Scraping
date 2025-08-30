# Iranian E-Commerce & Classifieds API Clients

This repository contains a collection of Python-based toolkits for interacting with the internal APIs of popular Iranian web platforms. Each client is designed to programmatically search, discover, and extract structured data, providing a more efficient and reliable alternative to traditional web scraping of HTML.

## 🚀 Projects

This collection currently includes the following clients:

-   **[Jabama API Client](/jabama_scraper):**
    A three-stage client for scraping accommodation data from Jabama. It allows for the discovery of search keywords, extraction of dynamic filters, and execution of targeted searches for properties.

-   **[Divar API Client](/divar_scraper):**
    A comprehensive four-stage client for Divar, Iran's largest classifieds platform. It systematically handles suggestion discovery, filter extraction, filtered ad searching, and the retrieval of full post details.

-   **[Digikala API Client](/digikala_scraper):**
    A powerful toolkit for the Digikala e-commerce platform. It features advanced product search with filters, autocomplete discovery for finding categories and brands, and detailed report generation for any product URL.

**For detailed instructions on installation and usage for each client, please refer to the `README.md` file located inside its respective project folder.**

## 🔧 Core Technology

-   **Language:** Python 3
-   **Primary Library:** `requests` for handling all HTTP API calls.
-   **Data Format:** All outputs are structured in clean, machine-readable `JSON` format.

## 💡 Purpose

This collection is designed for educational and research purposes to demonstrate modern API interaction and data extraction techniques. It serves as a strong portfolio piece showcasing the ability to reverse-engineer and interact with undocumented APIs in a structured, multi-stage workflow.

## 🤝 Contributing

Suggestions, bug reports, and contributions are highly welcome! Please feel free to open an issue or submit a pull request to enhance the projects.

## ⚠️ Disclaimer

These tools are not officially endorsed by the respective platforms (Jabama, Divar, Digikala). Users are solely responsible for complying with the terms of service of these websites. The developers assume no liability and are not responsible for any misuse of this software. Use it responsibly.
