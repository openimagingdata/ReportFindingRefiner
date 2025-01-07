import re
from typing import List, Tuple, Optional
from .data_models import Report, Fragment


class SectionSplitter:
    """
    Splits text into sections based on naive headings:
    e.g. "Header:", "Findings:", "Impression:".
    """

    def __init__(self):
        self.known_sections = ["Header:", "Findings:", "Impression:"]

    def split_into_sections(self, report_text: str) -> List[Tuple[Optional[str], str]]:
        """
        Returns a list of tuples (section_label, section_text).
        If no headings are found, returns one tuple with (None, entire_text).
        """
        pattern = r"(" + "|".join(map(re.escape, self.known_sections)) + r")"
        parts = re.split(pattern, report_text)
        results = []
        current_section_label = None
        current_text_chunks = []

        for part in parts:
            part_stripped = part.strip()
            if not part_stripped:
                continue

            if part in self.known_sections:
                # Save the previous chunk
                if current_section_label and current_text_chunks:
                    combined_text = " ".join(current_text_chunks).strip()
                    results.append((current_section_label, combined_text))
                # Update the label
                current_section_label = part_stripped
                current_text_chunks = []
            else:
                current_text_chunks.append(part_stripped)

        # Final chunk
        if current_section_label and current_text_chunks:
            combined_text = " ".join(current_text_chunks).strip()
            results.append((current_section_label, combined_text))

        if not results and report_text.strip():
            # No recognized sections, return entire text
            results.append((None, report_text.strip()))

        return results

    def create_smaller_fragments(
        self, section_fragments: List[Tuple[Optional[str], str]]
    ) -> List[Tuple[Optional[str], str]]:
        """
        Example splitting inside each section if needed.
        """
        smaller_fragments = []
        for label, text in section_fragments:
            if ':' in text:
                fragments = text.split(':')
                for i in range(1, len(fragments)):
                    fragment_text = (
                        fragments[i - 1].split()[-1] + ': ' + fragments[i].strip()
                    )
                    smaller_fragments.append((label, fragment_text.strip()))
            else:
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