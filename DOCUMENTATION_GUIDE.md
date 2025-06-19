# Guide to Obtaining AWS Well-Architected Framework Documentation

This guide explains how to legally and properly obtain AWS Well-Architected Framework documentation for use with this FAQ assistant tool.

## Legal Considerations

When using AWS documentation, it's important to:

1. **Respect Copyright**: AWS documentation is copyrighted by Amazon Web Services, Inc.
2. **Personal Use Only**: The documentation should be used for personal reference and learning only
3. **Attribution**: Always provide proper attribution to AWS as the source
4. **No Redistribution**: Do not redistribute the documentation in its original or modified form

## How to Download Documentation

### Method 1: Manual Download (Recommended)

1. Visit the [AWS Well-Architected Framework Documentation](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
2. For each section:
   - Access the online documentation page
   - Use your browser's "Save As" feature to save the page as HTML or plain text
   - Place saved files in the `raw_docs/` directory of this project

### Method 2: PDF Downloads

AWS provides PDF versions of their documentation:

1. Visit the [AWS Documentation Portal](https://docs.aws.amazon.com/)
2. Search for "Well-Architected Framework"
3. Look for PDF download options for each pillar
4. Download and place these PDFs in the `raw_docs/` directory

### Method 3: Using the Document Scraper (Use with Caution)

This repository includes a basic `document_scraper.py` script as an educational example. If you choose to use it:

1. Review the script carefully to understand what it does
2. Ensure you are complying with AWS's terms of service
3. Run the script only when necessary and at a reasonable rate
4. Review the downloaded content for accuracy and completeness

```bash
python document_scraper.py
```

## File Structure

Your `raw_docs/` directory should contain text files with AWS documentation content. The format should be straightforward text files with meaningful content. The file naming doesn't matter as long as they have `.txt` extensions.

Example structure:
```
raw_docs/
├── well_architected_overview.txt
├── security_pillar.txt
├── reliability_pillar.txt
└── ...
```

## Important Reminders

- **Do not commit** documentation files to any public repository
- This tool is for **educational purposes** only
- Always refer to the **official documentation** for the most current information
- The AWS Well-Architected Framework is regularly updated; consider refreshing your local documentation periodically

## Citation

When using information derived from AWS documentation in any published work, please use the following citation:

```
Amazon Web Services, "AWS Well-Architected Framework", AWS Documentation
https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
```
