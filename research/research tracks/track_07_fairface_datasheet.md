# Track 07 — FairFace Datasheet Draft
**Stream:** B (Report Generation) · **Priority:** 🟡 Medium · **Owner Focus:** Aaradhya (WP3)
**Estimated Time:** 30 min · **Feeds:** Report dataset section

## Instructions
1. Paste `CONTEXT.md` into Claude Desktop first
2. Then paste the prompt below
3. Save the output as `results/07_fairface_datasheet.md`

## Prompt

Using the "Datasheets for Datasets" framework (Gebru et al., 2018/2021), draft a complete datasheet for the FairFace dataset as used by BiasAperture. Answer every question in the framework:
1. **Motivation:** Why was FairFace created? Who funded it?
2. **Composition:** 108,501 images, 7 race groups, 2 gender groups, 9 age bins. What does each instance represent? Any missing data?
3. **Collection Process:** How were images collected? What consent process? Source: Flickr Creative Commons — what are the implications?
4. **Preprocessing/Cleaning:** MTCNN face alignment, 0.25 padding — document exactly
5. **Uses:** What has FairFace been used for? What should it NOT be used for?
6. **Distribution:** License, access method, GitHub repo
7. **Maintenance:** Who maintains FairFace? Update history?

Ground every answer in the Karkkainen & Joo 2021 WACV paper and the dchen236/FairFace GitHub repo.
