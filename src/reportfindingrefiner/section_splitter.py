import re
from typing import List, Tuple, Optional
from .data_models import Report, Fragment


class SectionSplitter:
    """
    Splits text into sections based on main headings (Header, Findings, Impression)
    and then further splits sections by colons for natural subsections.
    """

    def __init__(self):
        self.main_sections = ["Header:", "Findings:", "Impression:"]

    def split_into_sections(self, report_text: str) -> List[Tuple[Optional[str], str]]:
        """
        Returns a list of tuples (section_label, section_text).
        If no headings are found, returns one tuple with (None, entire_text).
        """
        pattern = r"(" + "|".join(map(re.escape, self.main_sections)) + r")"
        parts = re.split(pattern, report_text)
        results = []
        current_section_label = None
        current_text_chunks = []

        for part in parts:
            part_stripped = part.strip()
            if not part_stripped:
                continue

            if part in self.main_sections:
                if current_section_label and current_text_chunks:
                    combined_text = " ".join(current_text_chunks).strip()
                    results.append((current_section_label, combined_text))
                current_section_label = part_stripped
                current_text_chunks = []
            else:
                current_text_chunks.append(part_stripped)

        # Final chunk
        if current_section_label and current_text_chunks:
            combined_text = " ".join(current_text_chunks).strip()
            results.append((current_section_label, combined_text))

        if not results and report_text.strip():
            results.append((None, report_text.strip()))

        return results

    def create_smaller_fragments(
        self, section_fragments: List[Tuple[Optional[str], str]]
    ) -> List[Tuple[Optional[str], str]]:
        """
        Split sections by colons to create natural subsections.
        Preserves the original section label (Header/Findings/Impression).
        """
        smaller_fragments = []
        for label, text in section_fragments:
            if label == "Findings:" and ':' in text:
                # Split findings section by colons, preserving the parent section
                lines = text.split('\n')
                current_fragment = []
                
                for line in lines:
                    if ':' in line and not line.endswith(':'):
                        # If we have accumulated text, save it as a fragment
                        if current_fragment:
                            fragment_text = ' '.join(current_fragment).strip()
                            smaller_fragments.append((label, fragment_text))
                            current_fragment = []
                        # Add this line as a new fragment
                        smaller_fragments.append((label, line.strip()))
                    else:
                        current_fragment.append(line)
                
                # Add any remaining text
                if current_fragment:
                    fragment_text = ' '.join(current_fragment).strip()
                    smaller_fragments.append((label, fragment_text))
            else:
                # Keep Header and Impression sections as single fragments
                smaller_fragments.append((label, text.strip()))
                
        return smaller_fragments


def create_fragments_from_report(
    report: Report, section_splitter: SectionSplitter
) -> List[Fragment]:
    """
    1) Split the entire report text into sections.
    2) Possibly further split each section.
    3) Return a list of Fragment objects.
    """
    fragments = []
    sections = section_splitter.split_into_sections(report.text)
    smaller_fragments = section_splitter.create_smaller_fragments(sections)
    seq_num = 0

    for section_label, section_text in smaller_fragments:
        fragments.append(
            Fragment(
                report_id=report.id,
                section=section_label,
                sequence_number=seq_num,
                text=section_text,
                vector=None,
            )
        )
        seq_num += 1

    return fragments


def create_fragments_from_reports(
    reports: List[Report], section_splitter: SectionSplitter
) -> List[Fragment]:
    """
    Process a list of Report objects and return a list of Fragment objects.
    """
    all_fragments = []
    for r in reports:
        frags = create_fragments_from_report(r, section_splitter)
        all_fragments.extend(frags)
    return all_fragments