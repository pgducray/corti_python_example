import { CortiClient, CortiError } from "@corti/sdk";

const cortiClient = new CortiClient({
  auth: {
    accessToken: "<access-token>", // provide an access token retrieved by your authentication flow
  },
});

try {
  const response = await cortiClient.facts.extract({
    context: [{ type: "text", text: "Orthopedic Referral Letter\n\nDate: 2026-03-06\n\nReferring Clinician:\nPrimary Care Clinic\nCopenhagen, Denmark\n\nRe: Referral to Orthopedic Clinic — Evaluation of Chronic Knee Pain\n\nDear Orthopedic Colleague,\n\nI am referring a 62-year-old male patient for orthopedic evaluation of persistent right knee pain and functional limitation.\n\nHistory of Present Illness:\nThe patient reports progressive right knee pain for approximately 8 months. The pain is described as aching with intermittent sharp exacerbations during weight-bearing activities such as walking, stair climbing, and rising from a seated position. Symptoms have gradually worsened and now limit daily activities, including walking distances greater than 500 meters.\n\nHe also reports morning stiffness lasting approximately 20–30 minutes and occasional swelling of the knee joint. There is no history of acute trauma, locking, or mechanical instability. Over-the-counter analgesics (paracetamol and intermittent NSAIDs) provide only partial relief.\n\nPast Medical History:\n- Hypertension\n- Hyperlipidemia\n\nMedications:\n- Lisinopril 10 mg daily\n- Atorvastatin 20 mg daily\n- Paracetamol as needed for pain\n\nPhysical Examination (2026-03-01):\n- Mild joint effusion of the right knee\n- Tenderness along the medial joint line\n- Reduced range of motion due to pain\n- No ligamentous instability detected\n- Antalgic gait observed\n\nInvestigations:\nPlain radiographs of the right knee performed on 2026-02-25 demonstrate medial compartment joint space narrowing with osteophyte formation consistent with degenerative osteoarthritis.\n\nAssessment:\nChronic right knee pain consistent with medial compartment osteoarthritis.\n\nReason for Referral:\nGiven the patient's persistent symptoms despite conservative measures, I would appreciate your evaluation for further management options, including consideration of advanced nonoperative therapies or possible surgical intervention.\n\nAttachments:\n- Right knee X-ray report (2026-02-25)\n\nPlease let me know if any additional information is required. Thank you for your assessment of this patient.\n\nKind regards,\n\nPrimary Care Clinician\nPrimary Care Clinic\nCopenhagen, Denmark" }],
    outputLanguage: "en-US",
  });

  console.log("Extracted facts:", response.facts);
  console.log("Credits consumed:", response.usageInfo.creditsConsumed);
} catch (error) {
  if (error instanceof CortiError) {
    console.error("Error extracting facts:", error.body);
  } else {
    console.error("Unexpected error:", error);
  }
}
