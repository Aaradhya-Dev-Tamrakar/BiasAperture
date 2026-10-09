---
title: "Proposal Defense Transcript — BiasAperture"
date: 2026-09-07
time: "18:00 GMT+05:45"
duration: "~26 minutes"
format: Audio transcription (auto-generated)
presenters:
  - Aaradhya Dev Tamrakar
  - Tisha Manandhar
program: Fusemachines AI Fellowship (AIF) 2026
supervisor: Shreejan Kisee
status: Archived
---
# (Audio) AIF - Proposal Defence (Aaradhya Dev Tamrakar) - 2026\_09\_07 18\_00 GMT\+05\_45 - Recording (1)

[00:00:00] हुन्छ, start गरियो अन्त तिमारू? Share करें सर।

[00:00:16] ないな、だいぶ。 Uh, we will screen share also. Yes. So good evening, everyone. I'm Aravind Tamata, and, uh, today, together with my teammate, Shyam Ananda, I'll be presenting our proposed project, uh, Biasapator: A Diagnostic Framework for Demographic Bias Auditing in Facial Analysis Models. So this presentation covers the motivation behind the project, the problem we aim to solve, our objectives, and the research foundations, and finally, the proposed system architecture.

[00:00:53] Uh, facial analysis systems are increasingly used, uh, for tasks such as gender classification, [00:01:00] uh, age estimation, and demographic prediction. However, despite their, uh, widespread use, uh, research has consistently shown that their accuracy is not uniform across, uh, different demographic users-- groups. Uh, this raises an important question that how can we systematically detect and evaluate these, uh, disparities?

[00:01:19] This is the central motivation behind, uh, Biasapator. So a major empirical, uh, example is the Gender Shades study, which has reported, uh, substantially different error rates. As you can see, thirty-three point nine percent, uh, and, uh, above thirty-three percent, uh, error rate for the darker skin female and lighter skin male, uh, subjects.

[00:01:40] So, uh, the larger problem, however, is that most existing audits are conducted manually and only at a single point, and they are typically not reusable as a standardized software-based auditing service. Mm. These disparities can arise from multiple sources like, uh, [00:02:00] training data imbalance, uh, demographic proxies encoded through, uh, visual features, and insufficient subgroup evaluation during development.

[00:02:09] At the same time, the regulatory environment is becoming more demanding. Uh, frameworks such as EU AI Act create a growing need for systematic and well-documented bias assessment. Uh, this creates a significant engineering grap-gap between, uh, fair-fairness research and practical implementation. While fair many fairness metrics and, uh, research methods already exist, there is still a lack of, uh, an accessible, reusable, and stan-- and standardized platform that turns these methods into a repeatable auditing workflow for fairness facial analysis models Uh, our primary objective is to design a bias aperture as an end-to-end, uh, diagnostic, uh, and, uh, evaluative platform for [00:03:00] identifying accuracy disparities.

[00:03:03] The system is designed around these five main objectives: a model-- uh, a modular and model-agnostic architecture, a fairness, uh, evaluation using, uh, independent backends like, uh, AI360 and Fairlearn, and standardized and interpretable le-reporting, uh, validation dur-using the Fairface benchmark, and regulatory traceability, uh, through frameworks such as EU AI Act and NIST AI RMF.

[00:03:34] Um, you literature review table

[00:03:41] ஆ, ஆயிடுச்சு போயி.

[00:03:58] ए American मा [00:04:00] remote sharing गर्ने गथ्यो time second लाग्थ्यो कि त्यो भएर change गरेको थ्यो। Okay, no worries।

[00:04:18] अहिले आइराखेको छैन Ahí eres.

[00:04:27] Mayor. Y ya estaría

[00:04:33] So, uh, uh, continuing where we were. Our literature review, uh, established the scientific foundation of the platform. Uh, Gender Shades, uh, provides the basis for self-group and intersectional auditing. Hardt and, uh, uh, colleagues provide the theoretical, theoretical basis for fairness metrics such as equalized odds and, uh, equal opportunity.

[00:04:58] More recent research also highlights [00:05:00] that, mm, models may rely on unintended visual features mo-motivating the use of, uh, explainability methods, while other studies identify a clear gap in the practical auditing workflows Uh, for standardization and documentation, BiasFHR draws on two major conve-conventions, model cards and data sheets for datasets.

[00:05:24] For benchmarking, we use Fairface as, uh, mmm, because of its, uh, demographic repre-representation and suitability for subgroup-based evaluation. Uh, another important, uh, finding from the literature is that fairness thresholds, uh, should not be interpreted without statistical evidence, uh, like, uh, the forfeits thresholds, uh, does.

[00:05:47] And, uh, therefore, BiasFHR combines disparity metrics with statistical significance testing and confidence intervals. Research connecting regulatory requirements, uh, with technical, uh, verification also [00:06:00] informs our compliance with the traceability efforts. Uh, SHAP. The explainability, explainability component uses SHAP to identify, uh, which images, uh, image regions influence the model predictions.

[00:06:15] Uh, where, uh... However, we are-- we treat explainability carefully because, uh, though SHAP can provide evidence of influen-in-influential features, but it cannot prove causality and, uh, guarantee the complete absence of bias. Therefore, it-its use are, uh, uh, its findings are used as diagnostic signal rather than a definitive proof, proof for our project.

[00:06:37] Uh- The literature also shows that fairness cannot be represented by a single metric. For this reason, BiasAparture uses multi-complementary, uh, metrics and statistical validation. The platform focuses on, uh, specifically on, uh, model output bias, while dataset level bias and, uh, broader, [00:07:00] broader const-contextual factors remain important boundaries and potential areas for future work.

[00:07:09] Uh, so now I'd like to call, uh, Tisha for the next part of the presentation. Thank you, Aaranyya. Um, now I'll explain the architecture of BiasAparture and how the different modules work together. Um, the modules in our system architecture are data ingestion and pre-processing module, model interface module, fairness metrics engine, explainability layer, and the report generation module.

[00:07:38] The first module is the data ingestion and pre-processing module. It makes sure that the data entering the audit pipeline is valid and consistently represented. The module validates image integrity and standardizes image using OpenCV. More importantly, we convert the different dataset formats into a locked internal schema containing information such as image ID, race, [00:08:00] gender, age, and other demographic attributes, and the true label.

[00:08:04] This is important because different datasets can use different labeling conventions, which could introduce inconsistencies into the audit itself. Uh, the second module is the model interface module. It acts as a translator between the model and the fairness engine. The key idea here is that the fairness engine should not depend on a particular machine learning framework.

[00:08:25] We therefore define a common model interface with two different adapters, both ultimately producing the same structure: image ID, demographic attributes, true label, and the predicted label. The third module is the fairness and metrics computation engine. The process begins with cohort generation. The engine supports both unitary cohorts and intersectional cohorts.

[00:08:46] Before computation, a sample size gate checks whether each cohort has su-has sufficient observation and flags if they don't pass the check. For valid cohorts, we bo-- we compute our core four fairness metrics [00:09:00] using AIF three sixty and Fairlearn backends. Both independently cal-calculate the metrics, and the validation gate compares their results to detected unexpected computational differences.

[00:09:11] The validated results then enter the statistical rigor stage. After passing the statistical testing, the final results are fed to the explainability module and the compliance map reporting. One of the foundational pillars of the fairness metric engine are the four metrics that measure differ-- diff-- measure the different demographic dimensions of fairness.

[00:09:33] Uh, the demographic parity difference measures differences in positive prediction rates, while the disparate impact ratio expresses those differences as a ratio. Uh, equalized odds difference evaluates parity in both true positive as well as false, false positive rates, while the equalized opportunity difference focuses specifically on true positive parity.

[00:09:58] Um, to make sure [00:10:00] our fairness metrics are reliable, we use three statistical checks. First, subgroups with fewer than thirty samples are flagged because their metrics result may be unstable. Second, we use bootstrap resampling with thousand or more iterations to calculate ninety-five percent, uh, confidence intervals, which tells us how uncertain our metric estimate is.

[00:10:21] Finally, we use a chi-squared test with a significance level of zero point zero five to calculate the P-value and determine whether the observed demographic differences show a statistically significant association. Uh, the fourth module is the explainability module, which is the diagnostic component. We use SHAP to measure different image regions to con-- uh, we use SHAP to measure how different, uh, image regions contribute to the model's prediction.

[00:10:53] This allows us to investigate potential visual proxies such as background lighting, image quality, or [00:11:00] borders. To keep computation efficient, SHAP is selectively triggered when module three checks a disparity. And the final module is the re-report generation and compliance layer. The report automatically maps our fairness findings to relevant requirements of the EU AI Act, particularly areas such as risk management, data governance, technical documentation.

[00:11:23] It also maps the same evidence to NIST AI risk management framework using its four functions: govern, map, measure and manage. The final output is therefore a standardized traceable audit that connects technical fairness results, uh, with recognized regulatory and risk management frameworks Finally, the expected outcome of BiasAparture is a complete audit-ready fairness assessment rather than just a collection of metrics.

[00:11:52] The platform generates standardized HTML reports, including SHAP-based explainability visualizations, and also [00:12:00] incorporates structured model cards and data sheets to improve model and dataset transparency.

[00:12:08] Mm-hmm. There are, however, some limitations. Our findings are bounded by the coverage and the quality of benchmark datasets. SHAP-based explainability is also computationally expensive for a high-- for high-dimensional facial images. So we are currently testing a low-dimensional surrogate explanation approach as well.

[00:12:26] The current system supports PyTorch, TensorFlow, and CSV/JSON prediction inputs, while additional formats, such as ONNX, remain future work. Uh, looking ahead, we plan to extend BIAS Apartheid to additional protected attributes and continuous monitoring as well.

[00:12:46] To conclude, BiasDeparture bridges fairness research and practical AI governance by combining systematic di- systematic disparity detection, statistical validat- uh, statistical validance and explainability in an [00:13:00] independent auditing layer. Uh, this is the team behind the project, and thank you everyone for listening.

[00:13:09] Okay, thank you. Uh, nice presentation. I think, uh, it covers everything, every information we need, right? So, uh, additional をご覧ください。

[00:13:25] Um, no question, but a few comments. Uh, I, uh, are you just two guys in the team? Uh, yes. Yeah. Because the task you are undertaking is quite large, and I think you're gonna have trouble at initial split, that is to gather datasets. Do you have some idea where are, uh, at-- where are you, uh, getting the datasets from?

[00:13:47] Uh- Um, we're currently using Fairface dataset. Initially, we also planned to use UTKFace as well, but due to the label, [00:14:00] uh, label mapping issue and also due to it is not human annotated, so it was not reliable. So we've, uh, currently decided on using Fairface dataset and- Okay. Uh, so this first list, the dataset you mentioned, uh, does it have annotation present already?

[00:14:19] So- Yes. Okay. So how many, uh, images and labeled, uh, text are there? Uh, it has, uh, about, uh, over 90... almost 100,000 images, uh, image datasets with, uh, uh, nine age groups, seven racial groups, and two gender, all labeled manually. Okay. But I still do think you need some resources. Have you, uh, research on that subject matter, like, uh, uh, we need about this much resources to undertake this process?

[00:14:54] Like, uh, for example, uh, GPU is a major concern for your project, so have you thought [00:15:00] about it? No. I think last time we check, uh, the required GPU was, um, six G- uh, six GB GPU RAM or eight GB, which was sufficient in our, our devices. Okay. But still I'm a little bit skeptical, but, uh, this project you are undertaking is, uh, very impressive, and I wish you guys the best of luck.

[00:15:30] It's, uh... You, you will learn a lot if you complete this project too, so good luck, guys. Thank you.

[00:15:42] So from my side, uh, I just wanted to understand if, uh, the fairness... Basically, you are talking about the fairness, right? And I just wanted to understand if you were, uh, making it such that, uh, you are trying to [00:16:00] leverage already existing models and trying to check their own fairness, or you're trying to, uh, generate your own separate model?

[00:16:08] Uh, what is the actual concept behind it?

[00:16:13] We're leveraging existing fairness backends

[00:16:20] So for example, uh, you need, uh, some base model for image processing, right?

[00:16:31] So which kind of model are you thinking to use? Um

[00:16:38] Any idea on that or do you still, uh, have that field unexplored and you're thinking about exploring different models like ViT, uh, U-Net, ResNet? Any idea what

[00:16:57] Ri-- I think we're using, uh, [00:17:00] um, since we're using, uh, Fairne- Fairface's dataset, Fairface ResNet is being used Okay, इसमें से first में से हमने 10 साले बोले जैसे थोड़ा model try कर रहे हैं। है ना? अब ਦੇ बाद जैसे ही वो said we will try another models as well। So we are starting from the uh ResNet, right? Yeah, fair-fair case is ResNet 34.

[00:17:28] So basically here we won't be creating the models, but, uh, like, uh, we will taking the evaluating the models. Yeah, it-it's better to evaluate different model, not just ResNet. Uh, there are different, uh, uh, ResNets, uh, better to explore those and maybe try some other models and compare the scores because, uh, I think you have, uh, taken another metrics and another ob-- uh, objective metrics other than statistical score.

[00:17:56] That is a great approach. But- Mm-hmm. [00:18:00] ...yeah, uh, it's better to compare models and see how, um, how the result is and how, how the result is coming as, uh, as you have planned or expected. See the difference and map of the, uh, differences in, uh, of different approach. So- Mm-hmm. ...yeah, it's a good project. It's a very good project And again lots to do but there are only two of you so I'm little bit worried.

[00:18:29] So हाम्रो season time हुँदाखेरि मलाई self गर्न त लाग्ने

[00:18:37] They are pretty hard working so त्यस्तो केही issue होला जस्तो लाग्दैन मलाई।

[00:18:46] Actually म चाहिँ यसको basic concept को बारेमा सोध्न मन लाग्यो है। Basically हाम्रो यसमा चाहिँ pre-existing modelsहरूको चाहिँ अब कतिको fair, fairly judge गरिराको छ? Like if [00:19:00] there is a woman of color भनेको जस्तै। अब उनीहरूलाई चाहिँ हाम्रै examination लिएर होइन online examination लिएछम् भने चाहिँ त्यसको लागि that particular model लाई चाहिँ कतिको fair छ भनेर judge गर्ने concept हो होइन यसमा?

[00:19:16] Or- Facial कुनै पनि facial analysis model को task गर्दाखेरि चाहिँ त्यसले कति fairly सबै demographic subgroups लाई कति fairly judge गर्यो भनेर evaluate audit गर्नु। के यसमा मैले थपेन? त्यो evaluation सँगसँगै चाहिँ हामीले explainable part पनि थप्न खोजिरहेछौँ। Why it evaluated as it the-- it as जे होस् त्यो model ले गर्‍यो भनौँ न, होइन?

[00:19:44] त्यसमा चाहिँ किन चाहिँ उल्ले गर्‍यो भन्ने explainable part पनि राख्न खोजिरहेछौँ। तो... सो त्यसमा होइन, उनीहरूले चाहिँ के गर्छ भन्दाखेरि input image input दिन्छ होइन? Image input को firstमा original name उनीहरूले चाहिँ कुनै JSON or CSV मा save गर्छन् होइन? अब [00:20:00] result मा feed गर्नु भन्दा अगाडि त pre processing हुन्छ होइन?

[00:20:03] So rescaling हुन्छ, black and white गर्ने के के के हुन्छ, blurring गर्ने processing हुन्छ। उनीहरूले every processing को चाहिँ every detail चाहिँ CSV मा or JSON मा save गरेर राख्नुपर्छ क्या। अनि त्यसपछि उनारको त्यो जुन embedding छ, embedding लाई कसरी-- कसरी store गर्ने? अब छुट्टै folder मा store गरेर mapping गर्ने कसरी?

[00:20:25] यो अलि त्यही त अलि लामै हुन्छ क्या हो project अब। त्यही हो र मैले चाहिँ best of luck मात्रै भन्न सक्छु यसमा। पहिलेलाई चाहिँ video मै work गर्ने plan छ कि or images हरूमा नै मात्रै work गर्ने plan छ? Images नै हो अहिले त हामी काम गर्ने। अँ त्यही because since उनारले images मा चाहिँ audit गर्ने भन्ने concern राखेको छ, उन every stage को record गरेर कुन stage मा चाहिँ discrepancy आयो भनेर main figure out गर्नु पनि पऱ्यो नि त। Like अब bias नेस आयो है, हैन?

[00:20:59] अब bias नेस [00:21:00] आउँदाखेरि चाहिँ कुन stage मा गएर चाहिँ bias आयो भने उनारले त्यो figure out गर्न चाहिँ हल्का सोच्नुई पर्छ। Yeah, that's the hard part. मतलब अहिलेको चाहिँ, होइन, अब हाम्रो हिसाबले चाहिँ होइन, first एकदम high level मा जाँदाखेरि त्यही हामीले के सोचेको भन्दाखेरि चाहिँ अब AI मा bias छ कि छैन हामीले सुरुमा त्यो हेर्न खोज्यौँ होइन। त्यो चाहिँ ए special analysis models हरूमा चाहिँ अब कत्तिको biasing छ त?

[00:21:27] जस्तै चिन्न सक्छौँ है सक्दैन भन्ने कुरामा आयो नि त होइन। अनि अब हामीसँग भएको त्यो nine age seven races र two genders मा होइन, अब त्यतिमा चाहिँ त्यो model ले accuracy भन्न सक्छ कि सक्दैन भन्दा चाहिँ चारवटा core metrics को value अनुसार चाहिँ अब हामीले SAP चाहिँ use गरेको छैन अहिले। SAP surrogation, SAP को surrogate गरे use गरेको अहिले additive SAP को। अनि यसबाट चाहिँ AI मा चाहिँ bias छ कि छैन भन्दा हामीले चाहिँ कम्तीमा पनि तीस वटा [00:22:00] को चाहिँ sample use गर्छौँ क्या होइन, feed गर्ने बेलामा। अब त्यहाँबाट आएको output ले चाहिँ त्यस्तो detail मा नगइकन अहिलेको हाम्रो understanding अनुसार चाहिँ त्यस्तै तपाईँले भन्नुभको जस्तो, दिशल दाले भन्नुभको जस्तो त्यस्तो detail मा नगइकन त्यो तीस वटा sample dataset चाहिँ होइन, त्यसमा चाहिँ त्यो चारवटा value चाहिँ कस्तो आउँछ त भनेर त्यो model को output हेर्न खोजेको क्या एक हिसाबले अहिलेलाई चाहिँ होइन। अनि त्यो, त्यो त्यसबाट चाहिँ AI मा bias छ कि छैन भनेर हामीले explain गर्न खोजेको। as a अब यो complete नहोला तर अहिलेको चाहिँ chain of thought चाहिँ त्यस्तरी छ क्या अहिले। Okay, मैले बुझेँ होइन। La inference गर्ने stage मा होइन तिमीले त के-के चाहिँ input हुन्छ अनि expected output चाहिँ के हुन्छ?

[00:22:46] अब image मात्रै दिएर bias छ कि छैन भन्ने कुरा त it doesn't make sense नि त होइन। अँ। So अब कुन context मा image दिएको हो अनि त्यसलाई चाहिँ त्यो ए model ले चाहिँ कसरी लिएको छ चाहिँ? Inference style चाहिँ कस्तो छ? Input output को term छ भन न मलाई।[00:23:00] 

[00:23:07] त्यो मलाई भन्दा ति सरलाई बढी थाहा होला त्यो part मा चैँ। ओके अँ थाहा छैन भने थाहा छैन भने हुन्छ। Like we are in the research phase so त्यो बिस्तारै गर्दागर्दै चैँ थाहा हुने कुरा हो। अँ, मेरो understanding मा चाहिँ हैन अब तिमीहरूले भन्ने अनुसार चाहिँ कस्तो हुन सक्थ्यो भन्दाखेरि if there are-- we are making facial attendance system अरे हैन?

[00:23:33] यो चाहिँ मेरै आफ्नै experience बाट भनिराको हो। मैले चाहिँ पहिला कोज्रा भन्ने कम्पनीमा चाहिँ त्यो work गरेको थिएँ कि हैन? So basically facial attendance system चाहिँ त्यहाँको CCTV cameraबाट if there are thirty peoples जसको चाहिँ every day facial कुन time मा entry भयो र exit भयो भनेर पाइराको छ अरे हैन?

[00:23:53] त basically त्यो thirty वटा people को लागि चाहिँ thirty days week को thirty days को कतिवटा week छ, [00:24:00] त्यसबाट चाहिँ कतिजना मान्छेको actual आको छ र कतिजनालाई चाहिँ actually चाहिँ त्यो particular time आएकोमा चाहिँ recognize गरेर database मा चाहिँ register गर्‍यो। अनि त्यसबाट चाहिँ like depending on how they look or how like time lightingहरू तिनीहरूको basis मा चाहिँ fairnessहरू compare गर्ने type को concept हो कि...

[00:24:24] हैन, उनीहरूले चाहिँ मलाई चाहिँ के लाग्छ भन्दा उनीहरूले चाहिँ आफ्नो scopeलाई चाहिँ एकदम narrow down गर्नुपर्छ। के को कुरामा चाहिँ discrimination गर्ने, discrimination गर्ने हुन्छ नि? Scope चाहिँ उनीहरूको चाहिँ clear छैन जस्तो लाग्यो मलाई चाहिँ है। Discrimination, discrimination त भने, भनेको छ but के को context मा चाहिँ discrim-- अब like हुन्छ नि अब चोरहरू भन्यो भने चाहिँ त्यही कालेहरूलाई धेरै देखाइदिने हुन्छ कि हैन?

[00:24:48] Like त्यो चाहिँ resultsहरू हुन्छ नि कस्तो आइराको छ? Scope त अब चोरहरूको search गरेको छ कि हैन? Engineer गर्ने बेला Indianहरू मात्रै देखाइदिने खालको हुन्छ कि हैन? Engineer query [00:25:00] गर्ने बेला Ind-Indianहरू धेरै हुन्छन् त अब उनीहरूको dataset कस्तो छ त्यही अनुसार चाहिँ scope determine गर अनि त्यही, त्यही अनुसार चाहिँ inference गर भन्छु म चाहिँ। हो, हामीले अँ त्यो facial analysis modelहरूको चाहिँ कुन चाहिँ spe-specific scope हो त्यो एउटा pick गरेर चाहिँ गर्नुपर्छ भन्छु म चाहिँ है। अँ, एकदम। Since त्यो task specific भनेको हो भने। Exactly.

[00:25:27] Okay, like already सानै राखौं ल यो पछि हाम्रो अर्को पनि meeting छ। So अरू केही last question छ भने चाहिँ last गरुम् अनि चाहिँ यो meeting end गरुम्। अँ कसैको केही छ?

[00:25:45] छैन होला है? So हुन्छ like अडा टिसा अब काम गर्दै जुम्। अब गर्दा गर्दै like अब सिक्दै नै जाने हो है like बिचबिचमा अब फेरि हामी suggestionहरू लिँदै गर्छम्। I think रोनक र निक्सलले I think [00:26:00] यस्तै खाले projectहरू पनि गरिसकेको छ so in like बिचबिचमा हामी suggestion लिँदै गरौँ न। हुन्छ हैन रोनक, निक्सल? Of course, thank you.

[00:26:08] एकदम भाइ। Okay. So best of luck for your project. The idea is great so hopefully you learn a lot from this project as well.

