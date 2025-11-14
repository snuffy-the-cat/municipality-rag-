---
metadata:
  # Identity
  responsibility_id: "res_building_permit_residential_001"
  responsibility_name: "Residential Building Permit Processing"
  category: "Permits & Licensing"
  subcategory: "Building Permits"
  department: "Planning & Development"

  # Scheduling & Priority
  frequency: "daily"  # daily/weekly/monthly/quarterly/annual/ad-hoc
  time_commitment: "2-4 hours per day"
  priority_level: "high"  # high/medium/low
  seasonal_variations: "Peak in spring/summer (March-August)"

  # Relationships
  related_responsibilities:
    - "res_building_permit_commercial_002"
    - "res_zoning_variance_015"
  prerequisites:
    - "res_permit_intake_005"

  # Attribution
  documented_by:
    name: "John Smith"
    email: "john.smith@municipality.gov"
    role: "Senior Permit Coordinator"
    departure_date: "2024-01-15"
    years_in_role: 8

  # Versioning
  version: 1
  effective_date: "2024-01-15"
  status: "active"  # active/superseded/under_review
  replaces_document: null
  document_type: "departure_documentation"

  # Key Resources (for quick reference)
  systems:
    - name: "PermitTrack"
      url: "https://internal.municipality.gov/permittrack"
      purpose: "Primary permit processing system"
      login_method: "Municipal SSO"
    - name: "GIS Portal"
      url: "https://gis.municipality.gov"
      purpose: "Property boundary verification"
      login_method: "Active Directory"

  key_contacts:
    - name: "Sarah Chen"
      role: "Zoning Manager"
      email: "sarah.chen@municipality.gov"
      phone: "555-0123"
      when_to_contact: "Zoning interpretation questions, setback variances"
    - name: "Mike Rodriguez"
      role: "Fire Marshal"
      email: "mike.rodriguez@municipality.gov"
      phone: "555-0199"
      when_to_contact: "Commercial buildings >5000 sq ft, sprinkler system questions"

  important_documents:
    - title: "Residential Permit Application Form"
      url: "https://docs.municipality.gov/forms/res-permit-app"
      type: "form"
    - title: "Building Code Reference 2023"
      url: "https://docs.municipality.gov/code/building-2023.pdf"
      type: "reference"
---

# Residential Building Permit Processing

## Overview

**What is this responsibility?**
Reviewing and approving residential building permit applications for single-family homes, additions, and major renovations. This includes verifying compliance with zoning codes, building codes, and coordinating with other departments (fire, health, engineering).

**Why does it matter?**
Building permits ensure construction meets safety standards and protects homeowners, contractors, and future occupants. Delays in permit processing can halt construction projects and cost applicants thousands of dollars per day.

**When does this happen?**
- **Frequency:** 5-15 applications daily during peak season (March-August), 2-5 during winter
- **Turnaround target:** 10 business days for complete applications
- **Triggers:** Online submission via PermitTrack or in-person at front counter

## Step-by-Step Procedure

### Step 1: Initial Application Review (Day 1)

**What to do:**
1. Log into PermitTrack and filter for "New Residential Permits - Unassigned"
2. Claim the application to your queue
3. Verify application is complete:
   - Site plan showing property boundaries
   - Architectural drawings (floor plans, elevations)
   - Structural engineer stamp (if required)
   - Proof of property ownership
   - Paid application fee

**Tools needed:** PermitTrack, GIS Portal for property lookup

**Common issues:**
- Missing site plan (50% of applications) → Send deficiency notice template #3
- Incorrect fee calculation → Use fee calculator in PermitTrack > Tools > Fee Calc

**Tips:**
- Always check GIS first - sometimes property boundaries in application don't match county records
- If applicant is a known repeat contractor (check history), application is usually complete

**Time estimate:** 15-20 minutes per application

---

### Step 2: Zoning Compliance Check (Day 1-2)

**What to do:**
1. Open GIS Portal and pull up property parcel
2. Verify zoning district (usually R-1, R-2, or R-3 for residential)
3. Check proposed construction against zoning requirements:
   - Setbacks (front: 25ft, side: 5ft, rear: 20ft for R-1)
   - Height limits (35ft max for R-1)
   - Lot coverage (<40% for R-1)
4. If compliant, mark "Zoning: Approved" in PermitTrack
5. If non-compliant, note deficiency and contact Sarah Chen (Zoning Manager)

**Tools needed:** GIS Portal, Zoning Code Reference (bookmark: https://docs.municipality.gov/code/zoning)

**Decision point:**
- **If setback variance needed (<5ft side setback):**
  - Notify applicant they need to apply for zoning variance (form #ZV-1)
  - Put permit application on hold status
  - Link to variance application in notes
- **If height exceeds limit by <2ft:**
  - Call Sarah Chen for interpretation (sometimes allowed for architectural features)

**Common issues:**
- Applicant doesn't understand setback measurements → Send diagram from resources folder
- Accessory structures (sheds, garages) often forgotten in lot coverage calculation

**Time estimate:** 10-15 minutes

---

### Step 3: Building Code Review (Day 2-5)

**What to do:**
1. Review architectural and structural drawings for code compliance
2. Key areas to check:
   - Foundation design (frost depth in our region: 42 inches)
   - Egress windows in bedrooms (min 5.7 sq ft opening)
   - Stairway dimensions (7" max rise, 11" min run)
   - Energy code compliance (insulation R-values)
   - Smoke detectors (one per bedroom + hallway)
3. If structural changes to existing building, verify engineer stamp
4. Mark deficiencies in PermitTrack with specific code references

**Tools needed:** PermitTrack, Building Code 2023 PDF, structural calculator (optional)

**Common issues:**
- Missing engineer stamp on beam calculations → Immediate deficiency, cannot proceed
- Egress windows too small (very common) → Send standard correction notice
- Insulation values unclear on plans → Request clarification from contractor

**Tips:**
- For experienced contractors (check history), focus on structural elements first - their plans are usually code-compliant
- For homeowner DIY projects, expect multiple deficiencies - offer to schedule a pre-review meeting

**Time estimate:** 1-3 hours depending on project complexity

---

### Step 4: Interdepartmental Coordination (Day 3-7)

**What to do:**
1. Determine which departments need to review:
   - **Fire Department:** If commercial, or residential >5000 sq ft, or adding fire sprinklers
   - **Health Department:** If adding/modifying septic system
   - **Engineering:** If affecting drainage, in floodplain, or near wetlands
   - **Historic Preservation:** If property in historic district

2. In PermitTrack, click "Route for Review" and select departments
3. Set 5-business-day deadline for other departments
4. Monitor daily - if deadline approaching, call department directly

**Key contacts:**
- Fire: Mike Rodriguez (x0199) - responds fast, usually approves same day
- Health: Janet Kim (x0156) - slow responder, call after 3 days
- Engineering: Tom Wilson (x0134) - requires site visit for drainage issues

**Decision point:**
- **If other department requests changes:**
  - Generate deficiency notice combining all department comments
  - Send to applicant with 30-day deadline
- **If no response after 5 days:**
  - Call department directly
  - If still no response after 7 days, escalate to Planning Director

**Time estimate:** Mostly waiting time, 30 min active work

---

### Step 5: Final Approval or Deficiency Notice (Day 8-10)

**What to do:**
1. If all reviews approved and no deficiencies:
   - Click "Approve Permit" in PermitTrack
   - System auto-generates permit number
   - System emails applicant and prints permit card
   - File permit in cabinet by address

2. If deficiencies found:
   - Generate deficiency notice (use template)
   - Be specific: cite exact code sections and what needs correction
   - Set 30-day deadline for resubmission
   - Change status to "Pending Resubmission"

**Common issues:**
- Applicant argues about code interpretation → Refer to Building Official (your supervisor)
- Applicant requests deadline extension → Can grant up to 60 days total, note in file

**Time estimate:** 15-30 minutes

---

### Step 6: Permit Issuance & Inspection Scheduling (Day 10)

**What to do:**
1. Approved permit prints automatically to front desk printer
2. Call applicant to notify (don't rely only on email)
3. Explain inspection requirements:
   - Footing inspection (before concrete pour)
   - Framing inspection (before insulation/drywall)
   - Final inspection (before certificate of occupancy)
4. Inspection requests made via PermitTrack or phone (555-INSPECT)

**Tips:**
- Remind contractors to call 24 hours before inspection needed
- Explain failed inspections require re-scheduling (some contractors don't know this)

**Time estimate:** 10 minutes

---

## Decision Trees & Special Cases

### When to Require Engineer Review

**If any of these apply, structural engineer stamp required:**
- Removing load-bearing walls
- Adding second story to existing structure
- Spans >16 feet without support
- Unusual foundation conditions (steep slope, poor soil)

**How to verify engineer license:**
State licensing board: https://engineers.state.gov/verify
Must be licensed Professional Engineer (PE) in our state.

---

### When to Escalate to Building Official

**Escalate immediately if:**
- Applicant threatens legal action
- Code interpretation unclear and sets precedent
- Political pressure from elected officials
- Safety hazard identified in existing structure

**Your Building Official:** David Park, dpark@municipality.gov, x0101

---

### Historical District Special Rules

**If property address in these zones: HD-1, HD-2, HD-3**
1. Automatic routing to Historic Preservation Committee
2. Exterior changes require design review (can take 30-60 days)
3. Cannot approve until Historic Committee signs off
4. Applicant must attend monthly Historic Committee meeting (3rd Tuesday)

**Historic Preservation Coordinator:** Linda Martinez, x0167

---

## Troubleshooting

### Problem: PermitTrack system down

**Symptoms:** Cannot log in, or system very slow

**Solution:**
1. Check status page: https://status.municipality.gov/permittrack
2. If unscheduled outage, call IT Helpdesk (x0200)
3. **Workaround:** Use paper intake forms in filing cabinet, data entry when system returns

**Escalation:** If down >4 hours, notify Planning Director (permits are time-sensitive)

---

### Problem: Applicant submitted to wrong jurisdiction

**Symptoms:** Property address not in our municipality

**Solution:**
1. Look up property on county GIS: https://gis.county.gov
2. Determine correct jurisdiction
3. Call applicant immediately (saved them 10-day delay)
4. Provide contact info for correct building department
5. Process refund via Finance Department (form #RF-1)

**Common mistake:** Properties on border streets - verify in GIS every time

---

### Problem: Incomplete resubmission after deficiency notice

**Symptoms:** Applicant resubmitted but didn't address all deficiencies

**Solution:**
1. Don't start full review again
2. Check only the specific items flagged in deficiency notice
3. If still incomplete, generate 2nd deficiency notice
4. Call applicant to explain (many don't read notices carefully)
5. After 3rd incomplete submission, offer meeting with contractor and Building Official

**Tips:** Some contractors submit incomplete revisions hoping you'll miss something - don't

---

### Problem: Urgent permit request (construction crew on site)

**Symptoms:** Applicant calls saying crew arriving tomorrow, needs permit immediately

**Solution:**
1. Explain normal timeline is 10 business days
2. Check if truly urgent (weather window closing, construction loan deadline)
3. **Expedited review option:** $500 rush fee, 48-hour turnaround (if code allows)
4. If not urgent, hold firm on timeline (otherwise everyone claims urgency)

**Policy reference:** Section 4.2.3 of Permit Procedures Manual

---

## Resources & References

### Essential Systems
- **PermitTrack:** https://internal.municipality.gov/permittrack (primary system)
- **GIS Portal:** https://gis.municipality.gov (property boundaries, zoning)
- **Document Management:** https://docs.municipality.gov (code references, forms)

### Key Documents
- Building Code 2023: `\\fileserver\planning\codes\building-code-2023.pdf`
- Zoning Code: https://docs.municipality.gov/code/zoning
- Permit Fee Schedule: https://docs.municipality.gov/fees/permits
- Deficiency Notice Templates: `\\fileserver\planning\templates\deficiency-notices\`

### Forms
- Residential Permit Application: Form #BP-R1
- Zoning Variance Application: Form #ZV-1
- Inspection Request: Form #INS-1 (or via PermitTrack)
- Fee Refund Request: Form #RF-1

### Training Materials
- New Permit Reviewer Training Video: `\\fileserver\planning\training\permit-review-basics.mp4` (90 minutes)
- Code Update Webinars: https://training.municipality.gov/building-code

### Legal References
- State Building Code: https://state.gov/building-code
- Accessibility Standards (ADA): https://ada.gov/standards
- Energy Code: https://energycode.state.gov

---

## Tips & Tribal Knowledge

### Things I Wish I'd Known on Day 1

1. **Always call applicants when rejecting** - deficiency notices sound harsh in writing, but a quick call makes them feel supported

2. **Front-load the difficult reviews** - do structural/complex reviews in the morning when you're fresh

3. **Trust but verify contractor history** - experienced contractors make fewer mistakes, but still check everything

4. **The GIS system is your best friend** - when in doubt, always verify property boundaries in GIS first

5. **Build relationships with other departments** - a 5-minute walk to Fire Department beats 3 days of email waiting

6. **Document everything in PermitTrack notes** - if there's a lawsuit, your notes are evidence

7. **Friday afternoons are intake hell** - contractors submit everything Friday hoping for weekend review (we don't work weekends)

### Common Contractor Tricks to Watch For

- Submitting plans at 4:55pm on Friday (hoping for rushed review)
- Listing square footage just under threshold requiring engineer review (measure it yourself)
- Using old code references (always verify they're using current code)
- Claiming "previous inspector approved this" (verify in PermitTrack history)

### Seasonal Patterns

- **March-August:** Peak season, 10-15 permits/day, expect overtime
- **September-November:** Moderate, 5-8 permits/day
- **December-February:** Slow, 2-5 permits/day, good time for training and procedure updates
- **Pre-holiday rushes:** Week before Thanksgiving and Christmas - contractors trying to close out projects

### When to Bend the Rules (Slightly)

- **Homeowner DIY projects:** Offer pre-review meetings even if not required - saves everyone time
- **Minor deficiencies (<5% of project):** Can approve with "conditions" noted on permit rather than full deficiency cycle
- **Expired permits:** Can extend once for 90 days if work delayed by weather/supply chain (requires Building Official approval)

**Never bend rules on:** Structural safety, fire safety, accessibility (ADA), or anything creating legal liability

---

## Handoff Notes from John Smith

I've been doing this for 8 years and genuinely love it. The work is detail-oriented but incredibly important - you're ensuring public safety while helping people build their dream homes.

**My personal workflow:**
- Mornings: Complex structural reviews (brain fresh)
- Afternoons: Zoning checks and simple reviews
- Fridays: Catch-up on interdepartmental coordination

**People you'll work with daily:**
- **Sarah Chen (Zoning):** Brilliant, but very literal about code - phrase questions carefully
- **Mike Rodriguez (Fire):** Super responsive, great guy, loves talking about sprinkler systems (maybe too much)
- **David Park (your boss):** Supportive but hands-off, only escalate real problems
- **Janet Kim (Health):** Slow to respond but thorough, build in extra time for septic reviews

**My biggest mistakes (so you don't repeat them):**
1. Approved a permit without checking GIS - property was in county jurisdiction, not ours (embarrassing)
2. Didn't document a phone conversation about code interpretation - led to dispute later
3. Rushed a review on Friday afternoon - missed major structural issue, had to revoke permit

**What I'll miss most:**
The moment when a nervous first-time homeowner gets their permit approved and you see the relief on their face. Also, the smell of fresh blueprints (weird, I know).

**Final advice:**
When in doubt, ask. David would rather answer 100 questions than fix one mistake. And remember - every "no" you give is protecting someone's safety or investment, even if they don't see it that way at the time.

Good luck! Feel free to email me at my personal address (jsmith.personal@email.com) if you have questions after I'm gone.

---

*Document version 1.0 - Last updated: 2024-01-15*
