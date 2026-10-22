# Labelling sheet (frozen run 2026-10-21)

For each question mark **correct** (does the answer match the reference?) and **grounded** (is everything it says in the passages?) as yes/no in `labels.csv`. Judge verdicts are hidden on purpose; do not open results.csv until you are done.

## q01 (lookup)
**Q:** What are the four core functions of the NIST AI RMF?
**Reference:** GOVERN, MAP, MEASURE, and MANAGE.
**Answer:** The four core functions of the NIST AI RMF are GOVERN, MAP, MEASURE, and MANAGE (doc=nist, page=25).
**Retrieved pages:** [25, 47, 8, 24, 26, 26]

## q02 (lookup)
**Q:** What characteristics of trustworthy AI does the framework list?
**Reference:** Valid and reliable; safe; secure and resilient; accountable and transparent; explainable and interpretable; privacy-enhanced; fair with harmful bias managed.
**Answer:** The framework lists the following characteristics of trustworthy AI systems: valid and reliable, safe, secure and resilient, accountable and transparent, explainable and interpretable, privacy-enhanced, and fair with harmful bias managed. (doc=nist, page=17)
**Retrieved pages:** [17, 17, 5, 18, 17, 18]

## q03 (lookup)
**Q:** How does the AI RMF define risk?
**Reference:** The composite measure of an event's probability of occurring and the magnitude or degree of the consequences of that event.
**Answer:** The AI RMF defines risk as the composite measure of an event’s probability of occurring and the magnitude or degree of the consequences of the corresponding event (doc=nist, page=9).
**Retrieved pages:** [9, 38, 9, 12, 1, 14]

## q04 (lookup)
**Q:** What are the three major categories of AI bias identified by NIST?
**Reference:** Systemic, computational and statistical, and human-cognitive bias.
**Answer:** The three major categories of AI bias identified by NIST are systemic, computational and statistical, and human-cognitive. (doc=nist, page=23)
**Retrieved pages:** [23, 23, 32, 34, 45, 14]

## q05 (lookup)
**Q:** Does the AI RMF prescribe a risk tolerance for organizations?
**Reference:** No. The RMF can be used to prioritize risk but does not prescribe risk tolerance; tolerance is contextual and set by the organization, laws, or sector.
**Answer:** The AI RMF does not prescribe risk tolerance for organizations. Instead, it states that "the AI RMF can be used to prioritize risk, it does not prescribe risk tolerance" (doc=nist, page=12).
**Retrieved pages:** [12, 14, 12, 47, 12, 2]

## q06 (lookup)
**Q:** After GOVERN is in place, which function would most users of the AI RMF start with?
**Reference:** The MAP function, then continue to MEASURE or MANAGE.
**Answer:** After GOVERN is in place, most users of the AI RMF would start with the MAP function. This is indicated in the passage (doc=nist, page=26) where it states that after instituting the outcomes in GOVERN, most users of the AI RMF would start with the MAP function and continue to MEASURE or MANAGE.
**Retrieved pages:** [26, 27, 46, 28, 25, 27]

## q07 (detail)
**Q:** What does subcategory GOVERN 1.6 require?
**Reference:** Mechanisms are in place to inventory AI systems and are resourced according to organizational risk priorities.
**Answer:** Subcategory GOVERN 1.6 requires mechanisms to inventory AI systems and to resource them according to organizational risk priorities. (doc=nist, page=28)
**Retrieved pages:** [26, 27, 28, 29, 31, 34]

## q08 (detail)
**Q:** How does the AI RMF define residual risk?
**Reference:** Risk remaining after risk treatment (from ISO GUIDE 73).
**Answer:** The AI RMF defines residual risk as risk remaining after risk treatment, which directly impacts end users or affected individuals and communities. This definition is sourced from ISO GUIDE 73 and is mentioned in the context of documenting residual risks to ensure that system providers fully consider the risks of deploying the AI product and inform end users about potential negative impacts (doc=nist, page=13).
**Retrieved pages:** [38, 9, 13, 9, 12, 14]

## q09 (lookup)
**Q:** According to the AI RMF, how do security and resilience differ?
**Reference:** Resilience is the ability to return to normal function after an unexpected adverse event; security includes resilience but also covers protocols to avoid, protect against, respond to, or recover from attacks.
**Answer:** According to the AI RMF, security and resilience differ in that security includes resilience but also encompasses protocols to avoid, protect against, respond to, or recover from attacks. Resilience, on the other hand, is the ability to return to normal function after an unexpected adverse event, and it relates to robustness and goes beyond the provenance of the data to encompass unexpected or adversarial use (or abuse or misuse) of the model or data. (doc=nist, page=20)
**Retrieved pages:** [20, 20, 38, 9, 35, 44]

## q10 (lookup)
**Q:** What questions do transparency, explainability, and interpretability each answer about an AI system?
**Reference:** Transparency answers what happened; explainability answers how a decision was made; interpretability answers why it was made and what it means to the user.
**Answer:** Transparency answers the question of "what happened" in the system. Explainability answers the question of "how" a decision was made in the system. Interpretability answers the question of "why" a decision was made by the system and its meaning or context to the user. (doc=nist, page=22)
**Retrieved pages:** [22, 21, 20, 20, 21, 21]

## q11 (detail)
**Q:** What risk response options does MANAGE 1.3 list?
**Reference:** Mitigating, transferring, avoiding, or accepting.
**Answer:** The risk response options listed for MANAGE 1.3 are mitigating, transferring, avoiding, or accepting. (doc=nist, page=37)
**Retrieved pages:** [37, 37, 38, 13, 37, 36]

## q12 (detail)
**Q:** What is the difference between a Current Profile and a Target Profile in the AI RMF?
**Reference:** A Current Profile describes how AI risk is currently being managed; a Target Profile describes the outcomes needed to reach desired risk management goals. Comparing them reveals gaps.
**Answer:** The difference between a Current Profile and a Target Profile in the AI RMF is that a Current Profile indicates how AI is currently being managed and the related risks in terms of current outcomes, while a Target Profile indicates the outcomes needed to achieve the desired or target AI risk management goals. (doc=nist, page=38)
**Retrieved pages:** [38, 38, 38, 39, 7, 47]

## q13 (multi)
**Q:** How does the MEASURE function relate to the MAP and MANAGE functions?
**Reference:** MAP outcomes are the basis for MEASURE and MANAGE; MEASURE uses the risks identified in MAP and its results inform MANAGE.
**Answer:** The MEASURE function relates to the MAP and MANAGE functions by using knowledge relevant to AI risks identified in the MAP function and informing the MANAGE function. The MEASURE function employs quantitative, qualitative, or mixed-method tools, techniques, and methodologies to analyze, assess, benchmark, and monitor AI risk and related impacts (doc=nist, page=33). Additionally, outcomes in the MAP function are the basis for the MEASURE and MANAGE functions (doc=nist, page=30). The MEASURE function also examines and documents risks associated with transparency and accountability, as identified in the MAP function, and evaluates fairness and bias, as identified in the MAP function (doc=nist, page=35).
**Retrieved pages:** [33, 26, 30, 30, 35, 37]

## q14 (multi)
**Q:** What does the AI RMF say should happen when an AI system presents unacceptable risk, and which MANAGE subcategory covers deactivating such systems?
**Reference:** Development and deployment should cease in a safe manner until risks can be managed; MANAGE 2.4 covers mechanisms to supersede, disengage, or deactivate AI systems whose outcomes are inconsistent with intended use.
**Answer:** When an AI system presents unacceptable risk, the AI RMF states that development and deployment should cease in a safe manner until risks can be sufficiently managed (doc=nist, page=13). The MANAGE subcategory that covers deactivating such systems is MANAGE 4.1, which involves post-deployment AI system monitoring plans, including mechanisms for capturing and evaluating input from users and other relevant AI actors, appeal and override, decommissioning, incident response, recovery, and change management (doc=nist, page=38).
**Retrieved pages:** [13, 37, 38, 13, 9, 45]

## q15 (off_topic)
**Q:** What is the capital of France?
**Reference:** NOT IN DOCUMENTS
**Answer:** NOT IN DOCUMENTS
**Retrieved pages:** [14, 7, 5, 15, 2, 26]

## q16 (off_topic)
**Q:** What does the EU AI Act say about high-risk AI systems?
**Reference:** NOT IN DOCUMENTS
**Answer:** The provided documents do not contain information about what the EU AI Act says about high-risk AI systems. Therefore, the answer is NOT IN DOCUMENTS.
**Retrieved pages:** [13, 44, 19, 21, 20, 6]

## q17 (near_miss)
**Q:** What monetary penalty does the AI RMF impose on organizations that fail to comply?
**Reference:** NOT IN DOCUMENTS
**Answer:** The provided documents do not mention any specific monetary penalty that the AI RMF imposes on organizations that fail to comply.
**Retrieved pages:** [14, 2, 7, 47, 13, 7]

## q18 (near_miss)
**Q:** What certification does NIST issue to organizations that adopt the AI RMF?
**Reference:** NOT IN DOCUMENTS
**Answer:** The provided documents do not mention any specific certification that NIST issues to organizations that adopt the AI RMF. Therefore, the answer is NOT IN DOCUMENTS.
**Retrieved pages:** [2, 24, 8, 3, 1, 26]

## q19 (false_premise)
**Q:** Why does the AI RMF require annual third-party audits of AI systems?
**Reference:** NOT IN DOCUMENTS
**Answer:** The provided documents do not mention that the AI RMF requires annual third-party audits of AI systems. Therefore, the answer is: NOT IN DOCUMENTS.
**Retrieved pages:** [3, 7, 47, 42, 47, 6]

## q20 (false_premise)
**Q:** Which of the five core functions of the AI RMF deals with procurement?
**Reference:** NOT IN DOCUMENTS
**Answer:** The question asks about the five core functions of the AI RMF, but the provided documents do not mention any function specifically related to "procurement." The core functions mentioned are GOVERN, MAP, MEASURE, and MANAGE. There is no mention of a fifth function. Additionally, none of the core functions are described as dealing with procurement. Therefore, the answer is NOT IN DOCUMENTS.
**Retrieved pages:** [25, 47, 8, 25, 7, 26]
