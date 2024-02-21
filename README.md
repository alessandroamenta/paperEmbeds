# ML Conference Paper Explorer 📄🔭

Efficiently find and explore papers from all the major ML conferences. Our tool aggregates accepted papers, enriches them with semantic embeddings for precise searching, and provides sleek visualizations for a straightforward experience. Forget the clunky official sites; our aim is to streamline your search for ML papers that are relevant to you.

## Features 🌟

- Semantic search for easy discovery of ML papers.
- Interactive t-SNE plots for visual exploration of paper clusters.
- Abstracts and titles converted to embeddings for nuanced search capabilities.
- A growing repository of papers from major ML conferences, stored for quick keyword searching.

## How to Use 🛠

1. Clone the repository to your local machine.
2. Set up a virtual environment and install dependencies from `requirements.txt`.
3. Run the Streamlit app with `streamlit run app.py`.
4. Search and explore papers using intuitive filters and semantic search.

## Extending the Tool with New Conferences 🌐

Want to add a new ML conference to our collection? Once you've developed the scraper and fetcher for the conference, you'll need to use and run `cli.py` to scrape and store the papers. Here's how you can do it:

### Scrape and Store Papers

To scrape and store papers for a new conference, use the following command, substituting the `conference_type`, `year`, `url`, and `num_papers` with the appropriate values for the conference you are adding, like in the example below:

```bash
python cli.py scrape --conference_type ICCV --year 2023 --url "https://openaccess.thecvf.com/ICCV2023?day=all"  --num_papers 5
```

### Embed Papers
After scraping, run the following command to create embeddings for the papers, which enhances the search capability:

```bash
python cli.py embed
```
If you need to start embedding from a specific index due to a large number of papers, use the --start_index option:

```bash
python cli.py embed --start_index 3600
```

Please ensure that your contributions follow the same coding standards and structure as the existing scrapers and fetchers. Happy coding!

## Conferences 📅

Progress on ML conference integrations:

| Conference | Year | Status          |
|------------|------|-----------------|
| ICCV       | 2023 | ✅              |
| NeurIPS    | 2023 | ✅              |
| CVPR       | 2023 | ✅              |
| EMNLP      | 2023 | ✅              |
| WACV       | 2024 | ✅              |
| ICLR       | 2024 | ✅              |
| AAAI       | 2024 | 🚧 In Progress  |
| NeurIPS    | 2024 | 📅 Planned      |
| IEEE       | 2024 | 📅 Planned      |
| AICS       | 2024 | 📅 Planned      |
| ECCV       | 2024 | 📅 Planned      |

## To-Do 📝

- [ ] Retrieve full vector data from Pinecone (current limit is 10k; we have 10,683 vectors).
- [ ] Enhance the unified search for a more intuitive experience, akin to Gmail's search capabilities.
- [ ] Complete the AAAI parser and fetcher for paper data.
- [ ] Containerize the application for easier deployment.
- [ ] Utilize Docker Compose or K3s for local spin-up of the app and database.
- [ ] Self-host an open-source vector database.
- [ ] Refine the interactive plot aesthetics and include category-based color coding.

## Contributing 🤝

Keen to chip in? Fork the project, make your changes, and submit a pull request! We're all about collaboration here. Check out the `CONTRIBUTING.md` for more details on how to get started.

## License 📜

The ML Conference Paper Explorer is open-source under the [MIT License](LICENSE).

Happy coding! 😊
