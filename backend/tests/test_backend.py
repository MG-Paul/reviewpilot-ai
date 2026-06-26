import pytest
import sys
import os

# Append backend directory to path so tests can run
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.import_parser import parse_ris, parse_bibtex
from app.services.deduplication import levenshtein_similarity, normalize_title, generate_mock_embedding
from app.agents.screening_agent import run_ai_screening
from app.agents.extraction_agent import run_data_extraction

def test_ris_parser():
    ris_content = """
TY  - JOUR
TI  - AI-assisted systematic reviews in clinical medicine: A validation study
AB  - Objective: To evaluate the performance of systematic review automation tools. Methods: A retrospective cohort study...
AU  - Smith, John
AU  - Doe, Jane
JO  - Journal of Medical Informatics
PY  - 2025
DO  - 10.1016/j.jmi.2025.01.002
VL  - 42
IS  - 3
SP  - 150
EP  - 159
ER  - 
"""
    results = parse_ris(ris_content)
    assert len(results) == 1
    ref = results[0]
    assert ref["title"] == "AI-assisted systematic reviews in clinical medicine: A validation study"
    assert ref["year"] == 2025
    assert "Smith, John" in ref["authors"]
    assert "Doe, Jane" in ref["authors"]
    assert ref["journal"] == "Journal of Medical Informatics"
    assert ref["doi"] == "10.1016/j.jmi.2025.01.002"
    assert ref["volume"] == "42"
    assert ref["issue"] == "3"
    assert ref["pages"] == "150-159"

def test_bibtex_parser():
    bib_content = """
@article{Smith2025,
  author = {Smith, John and Doe, Jane},
  title = {AI-assisted systematic reviews in clinical medicine: A validation study},
  journal = {Journal of Medical Informatics},
  year = {2025},
  volume = {42},
  number = {3},
  pages = {150-159},
  abstract = {Objective: To evaluate the performance of systematic review automation tools...},
  doi = {10.1016/j.jmi.2025.01.002}
}
"""
    results = parse_bibtex(bib_content)
    assert len(results) == 1
    ref = results[0]
    assert ref["title"] == "AI-assisted systematic reviews in clinical medicine: A validation study"
    assert ref["year"] == 2025
    assert len(ref["authors"]) == 2
    assert ref["authors"][0] == "Smith, John"
    assert ref["journal"] == "Journal of Medical Informatics"
    assert ref["doi"] == "10.1016/j.jmi.2025.01.002"

def test_levenshtein_similarity():
    # Identical titles after normalization
    t1 = "AI-assisted systematic reviews in clinical medicine"
    t2 = "AI-Assisted Systematic Reviews in Clinical Medicine!!!"
    assert levenshtein_similarity(t1, t2) == 1.0
    
    # Slightly modified title
    t3 = "AI-assisted systematic reviews in clinic medicine"
    assert levenshtein_similarity(t1, t3) > 0.90
    
    # Completely different title
    t4 = "Randomized trial of drug X vs placebo in hypertension"
    assert levenshtein_similarity(t1, t4) < 0.30

@pytest.mark.asyncio
async def test_screening_agent():
    # Setup test criteria (PICOS)
    picos = {
        "population": ["hypertension", "high blood pressure"],
        "intervention": ["drug X", "medication Y"]
    }
    
    # Match scenario
    title = "Efficacy of Drug X in Hypertension patients"
    abstract = "A randomized trial evaluating the impact of drug X on hypertension."
    match_result = await run_ai_screening(title, abstract, picos)
    assert match_result["decision"] == "include"
    
    # Miss scenario (wrong population)
    title_miss = "Efficacy of Drug X in asthma patients"
    abstract_miss = "A randomized trial evaluating the impact of drug X on asthma."
    miss_result = await run_ai_screening(title_miss, abstract_miss, picos)
    assert miss_result["decision"] == "exclude"
    assert miss_result["reason_code"] == "wrong_population"

@pytest.mark.asyncio
async def test_extraction_agent():
    text = "We conducted a randomized controlled trial. Total enrolled sample size was n = 120 patients."
    schema = [
        {"name": "sample_size", "type": "number", "description": "Total sample"},
        {"name": "study_design", "type": "string", "description": "Type of trial"}
    ]
    extracted = await run_data_extraction(text, schema)
    assert extracted["sample_size"]["value"] == "120"
    assert "Randomized Controlled Trial" in extracted["study_design"]["value"]
