
# modules/compliance_checker.py
import logging
import re

logger = logging.getLogger(__name__)

def check_youtube_description_compliance(description: str) -> list[str]:
    """Проверяет описание YouTube на потенциальные нарушения политик."""
    logger.info("Checking YouTube description compliance")
    issues = []
    
    # Примеры простых проверок
    if re.search(r'free.*money|get rich quick', description, re.IGNORECASE):
        issues.append("Potential spam/scam language detected.")
    
    if re.search(r'buy.*now|click.*here|limited.*offer', description, re.IGNORECASE):
        issues.append("Potentially aggressive marketing language detected.")
    
    # Проверка длины описания (YouTube ограничивает до 5000 символов)
    if len(description) > 5000:
        issues.append(f"Description too long: {len(description)} characters (max 5000).")
    
    if not issues:
        logger.info("✅ YouTube description compliance check passed")
    else:
        logger.warning(f"⚠️ YouTube description compliance issues: {issues}")
    
    return issues

def check_amazon_kdp_compliance(book_content: str) -> list[str]:
    """Проверяет содержимое книги на потенциальные нарушения политик Amazon KDP."""
    logger.info("Checking Amazon KDP content compliance")
    issues = []
    
    # Примеры простых проверок
    if re.search(r'adult content|explicit material', book_content, re.IGNORECASE):
        issues.append("Potential adult content detected.")
    
    if re.search(r'copyright|plagiarism', book_content, re.IGNORECASE):
        issues.append("Potential copyright issues detected.")
    
    # Проверка на слишком много ссылок
    link_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                                book_content))
    if link_count > 5:
        issues.append(f"Too many external links: {link_count} (recommended: max 5).")
    
    if not issues:
        logger.info("✅ Amazon KDP content compliance check passed")
    else:
        logger.warning(f"⚠️ Amazon KDP content compliance issues: {issues}")
    
    return issues

def check_general_compliance(content: str) -> list[str]:
    """Общая проверка контента на потенциальные проблемы."""
    logger.info("Performing general compliance check")
    issues = []
    
    # Проверка на чрезмерное использование заглавных букв (CAPS LOCK)
    caps_ratio = sum(1 for c in content if c.isupper()) / (len(content) + 1)
    if caps_ratio > 0.3:
        issues.append("Excessive use of capital letters detected.")
    
    # Проверка на чрезмерное количество восклицательных знаков
    exclamation_count = content.count('!')
    if exclamation_count > 10:
        issues.append(f"Too many exclamation marks: {exclamation_count}.")
    
    if not issues:
        logger.info("✅ General compliance check passed")
    else:
        logger.warning(f"⚠️ General compliance issues: {issues}")
    
    return issues
