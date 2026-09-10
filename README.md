# generate-dirty-files
================================================================================
PROJECT: SYNTHETIC DIRTY DATA GENERATOR
================================================================================

OVERVIEW:
---------
This project generates synthetic datasets with intentional data quality issues
for the purpose of practicing data cleaning and data wrangling techniques. 
The generator creates "dirty" files by introducing realistic corruption patterns 
that simulate real-world messy data scenarios.


PROJECT PURPOSE:
----------------
- Create datasets with controlled data quality problems
- Practice and develop data cleaning skills
- Test data validation and sanitization pipelines
- Simulate common file naming and content corruption patterns


TECHNOLOGIES USED:
------------------
- Python 3.x: Core language for all data generation logic
- Standard Library Modules:
  * os: Directory and file path operations
  * shutil: File copying and directory management
  * random: Stochastic file generation and corruption simulation


CORE TECHNIQUES & CORRUPTION METHODS:
-------------------------------------

1. FILENAME CORRUPTION:
   - Random name additions: _final, _old, _new, _copy, _backup, _draft
   - Capitalization modifications: UPPERCASE or Capitalized variations
   - Mistaken punctuation: Random insertion of _, -, . into filenames
   - Examples: invoice_old.txt, BUDGET_copy.csv, photo-report.json

2. CONTENT MUTATION:
   - Random content alteration based on configurable corruption rates
   - Duplicate file generation with optional secondary corruption
   - In-place file modification to create realistic data degradation
   - Probabilistic corruption application (configurable hit rates)

3. FILE TYPE DIVERSITY:
   - Multi-format support: .txt, .csv, .html, .json, .xml
   - Template-based generation ensuring consistent structure
   - Automatic extension discovery from base templates directory


PROJECT STRUCTURE:
------------------
config.py
  - Configuration constants (output directory, number of files)

main.py
  - Simple entry point for basic dirty file generation
  - Uses generate_title module directly
  - Creates text-based output files

master_generator.py
  - Advanced batch generation engine
  - Class-based architecture (MasterDataCorruptor)
  - Orchestrates template loading, filename generation, content mutation
  - Supports duplicate file creation with chained corruption
  - Highly configurable with parameters for output location, file count, 
    and corruption rates

base_templates/
  - base_csv.csv: Template for comma-separated value files
  - base_html.html: Template for HTML documents
  - base_json.json: Template for JSON structured data
  - base_txt.txt: Template for plain text files
  - base_xml.xml: Template for XML markup files

data_modifiers/
  - generate_title.py: Filename corruption and generation logic
    * Combines random file names with corruption modifications
    * Applies name additions, capitalization, and punctuation errors
  - generate_content.py: Content mutation engine (primary content corruptor)

modifiers/
  - capitals.py: Capitalization-related modifications
  - mistakes.py: Error and corruption pattern definitions


USAGE EXAMPLES:
---------------

Basic Usage (main.py):
  python3 main.py
  - Generates 20 corrupt files in ./output directory
  - Simple text-based generation with filename corruption only

Advanced Batch Generation (master_generator.py):
  python3 master_generator.py
  - Generates 40 files with multiple template types
  - 20% content corruption rate
  - 10% duplicate file generation rate
  - Creates diverse file formats with corruption patterns
  - Output to ./test_corrupted_batch directory


CONFIGURATION PARAMETERS:
------------------------

main.py:
  - AMOUNT_OF_FILES: Number of files to generate (default: 20)
  - OUT_DIRECTORY: Output folder path (default: "output")

master_generator.py:
  - templates_dir: Path to base templates directory
  - output_dir: Destination folder for generated files
  - total_files: Total number of files to create
  - corruption_chance: Probability of content mutation (0.0-1.0)
  - duplicate_chance: Probability of creating duplicate files (0.0-1.0)


KEY FEATURES:
-------------

1. TEMPLATE-BASED GENERATION
   - Automatically discovers available file format templates
   - Supports multiple file extensions simultaneously
   - Ensures consistent file structure across corruption scenarios

2. PROBABILISTIC CORRUPTION
   - Configurable corruption rates for fine-tuned data quality levels
   - Independent probability settings for content and duplicates
   - Realistic distribution of corruption patterns

3. DUPLICATE FILE HANDLING
   - Automatic detection and creation of duplicate files
   - Variants include: _copy, (1), _v2, _backup suffixes
   - Optional secondary corruption on duplicates

4. CONSOLE LOGGING
   - Detailed feedback on corruption operations
   - Real-time progress tracking during batch generation
   - Visual indicators for applied modifications


USE CASES:
----------

Data Cleaning Portfolio Projects:
  - Demonstrate data quality assessment skills
  - Build practical data cleaning pipelines
  - Test automated data validation workflows
  - Create before/after examples for case studies

Educational Purposes:
  - Learn data wrangling techniques
  - Practice file I/O operations in Python
  - Understand common data quality issues
  - Develop robust data handling strategies

Testing & QA:
  - Generate test datasets for data pipelines
  - Validate data cleaning tool robustness
  - Create various corruption test scenarios
  - Test data pipeline robustness


OUTPUT CHARACTERISTICS:
----------------------

- Multiple file formats: Plain text, CSV, HTML, JSON, XML
- Filename variations: Capitalization, punctuation errors, suffix additions
- Duplicate files: Same content with variant filenames
- Realistic corruption patterns: Mimics real-world data quality issues


DEPENDENCIES:
-------------
- Python 3.6+
- No external libraries required (uses standard library only)


KNOWN ISSUES:
-------------
- The generate_content.py file is currently empty and needs implementation 
  for full content mutation functionality


FUTURE ENHANCEMENTS:
--------------------
- Implement generate_content.py for advanced content mutation
- Add column-level corruption for CSV files
- Implement tag/attribute corruption for XML/HTML
- Add character encoding issues
- Introduce partial file truncation
- Support custom corruption plugins


================================================================================
Created for the Python Freelance Portfolio - Data Cleaning Project
================================================================================
