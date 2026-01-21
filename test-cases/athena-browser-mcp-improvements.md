# Athena Browser MCP - Improvement Test Cases

## Overview

This document contains manual test cases for verifying 7 proposed improvements to the athena-browser-mcp tool. Each improvement addresses issues discovered during Apple Store checkout automation.

**Test Environment:**
- URL: https://www.apple.com/shop/buy-iphone/iphone-17
- Browser: Chromium (headless or visible)
- MCP Server: athena-browser-mcp-local

---

## Issue #1: Clearer Element State Attributes

**Problem:** Current attributes like `e="0"` are cryptic and hard to understand.

### TC-1.1: Verify enabled/disabled state uses full words

**Preconditions:**
- Browser launched and navigated to iPhone 17 buy page
- No options selected yet

**Steps:**
1. Call `find_elements` with `kind: "radio"`
2. Examine the attributes on disabled radio buttons (payment, carrier, applecare options)

**Expected Result:**
```xml
<rad id="xxx" enabled="false" checked="false" val="fullprice">Buy...</rad>
```

**Actual Result (Current):**
```xml
<rad id="xxx" e="0" val="fullprice">Buy...</rad>
```

**Pass Criteria:** Attribute should be `enabled="false"` not `e="0"`

---

### TC-1.2: Verify checked state uses full words

**Preconditions:**
- Browser on iPhone 17 page
- Black color selected

**Steps:**
1. Call `find_elements` with `kind: "radio"`, `label: "Black"`
2. Examine the checked attribute

**Expected Result:**
```xml
<rad id="xxx" enabled="true" checked="true" val="black">Black</rad>
```

**Actual Result (Current):**
```xml
<rad id="xxx" chk="1" val="black">Black</rad>
```

**Pass Criteria:** Attribute should be `checked="true"` not `chk="1"`

---

### TC-1.3: Verify required field indication

**Preconditions:**
- Browser on a page with HTML `required` attributes (e.g., GitHub signup page)
- Note: Apple Store uses JavaScript validation, not HTML `required` attributes

**Steps:**
1. Call `find_elements` on form fields
2. Call `get_node_details` on a required field
3. Check if required fields are marked in both outputs

**Expected Result:**
```xml
<!-- In find_elements -->
<match eid="xxx" kind="radio" ... required="true" val="noTradeIn" />

<!-- In get_node_details -->
<state visible="true" enabled="true" required="true" />
```

**Actual Result (Tested on GitHub signup 2025-01-17):**
- `get_node_details`: Shows `<state visible="true" enabled="true" required="true" />`
- `find_elements`: Does NOT include `required` attribute in output

**Pass Criteria:** Required fields should have `required="true"` attribute

**Status: PARTIAL** - `required` is available in `get_node_details` but not exposed in `find_elements` output

---

## Issue #2: Form Validation Summary

**Problem:** No visibility into overall form state and what's blocking submission.

### TC-2.1: Verify form status summary after page load

**Preconditions:**
- Browser launched and navigated to iPhone 17 buy page
- Fresh page load, no selections

**Steps:**
1. Call `capture_snapshot` or `form_detect`
2. Look for form status summary in response

**Expected Result:**
```xml
<form_status form_id="iphone-config">
  <field name="color" status="required" selected="none" enabled="true" />
  <field name="storage" status="required" selected="none" enabled="true" />
  <field name="trade-in" status="required" selected="none" enabled="false" depends_on="storage" />
  <field name="payment" status="required" selected="none" enabled="false" depends_on="trade-in" />
  <field name="carrier" status="required" selected="none" enabled="false" depends_on="payment" />
  <field name="applecare" status="required" selected="none" enabled="false" depends_on="carrier" />
  <submit_button enabled="false" blocking_fields="color,storage,trade-in,payment,carrier,applecare" />
</form_status>
```

**Actual Result (Tested 2026-01-17):**
```xml
<!-- capture_snapshot returns: -->
<state step="3" title="Buy iPhone 17 - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="false">
    <mutations>
      <status id="rd-296f546b4b" role="text">AppleCare+ with Theft and Loss</status>
      <!-- ... text mutations only, no form status ... -->
    </mutations>
  </diff>
</state>

<!-- find_elements returns individual elements with enabled attribute, but no form summary -->
<match eid="995c309fb0e8" kind="radio" label="Lavender" enabled="true" val="lavender" />
<match eid="87d12aeb2810" kind="radio" label="256GB..." enabled="false" val="256gb" />
```

**Pass Criteria:** Form status summary should be included in snapshot/form_detect response

**Status: FAIL** - No `<form_status>` section provided in any response

---

### TC-2.2: Verify form status updates after selection

**Preconditions:**
- Browser on iPhone 17 page
- Color (Black) and Storage (512GB) already selected

**Steps:**
1. Click "No trade-in" option
2. Call `capture_snapshot`
3. Check form status summary

**Expected Result:**
```xml
<form_status form_id="iphone-config">
  <field name="color" status="complete" selected="Black" />
  <field name="storage" status="complete" selected="512GB" />
  <field name="trade-in" status="complete" selected="No trade-in" />
  <field name="payment" status="required" selected="none" enabled="true" /> <!-- NOW ENABLED -->
  <field name="carrier" status="required" selected="none" enabled="false" depends_on="payment" />
  <field name="applecare" status="required" selected="none" enabled="false" depends_on="carrier" />
  <submit_button enabled="false" blocking_fields="payment,carrier,applecare" />
</form_status>
```

**Actual Result (Tested 2026-01-17):**
```xml
<!-- After selecting Black, 512GB, No trade-in -->
<!-- capture_snapshot returns: -->
<state step="7" title="Buy iPhone 17 - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="true">
  </diff>
  <observations>
    <since_previous>
      <appeared significance="3" age_ms="5603">
        <content tag="span">$41.62/mo.  per month</content>
      </appeared>
      <!-- ... observations only, no form status ... -->
    </since_previous>
  </observations>
</state>
```

**Pass Criteria:** Form status should reflect current state and show newly enabled fields

**Status: FAIL** - No form status summary after selections. Diff shows text mutations but not field completion status.

---

### TC-2.3: Verify submit button enablement tracking

**Preconditions:**
- Browser on iPhone 17 page
- All options selected (color, storage, trade-in, payment, carrier, applecare)

**Steps:**
1. Call `capture_snapshot`
2. Check form status and submit button state

**Expected Result:**
```xml
<form_status form_id="iphone-config">
  <field name="color" status="complete" selected="Black" />
  <field name="storage" status="complete" selected="512GB" />
  <field name="trade-in" status="complete" selected="No trade-in" />
  <field name="payment" status="complete" selected="Buy" />
  <field name="carrier" status="complete" selected="Unlocked" />
  <field name="applecare" status="complete" selected="No AppleCare" />
  <submit_button enabled="true" label="Add to Bag" eid="18eb7ccd357c" />
</form_status>
```

**Actual Result (Tested 2026-01-17):**
```xml
<!-- capture_snapshot returns: -->
<state step="11" title="Buy iPhone 17 512GB Black - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="true">
  </diff>
</state>

<!-- find_elements for Add to Bag button returns: -->
<match eid="31f426071430" kind="button" label="Add to Bag" region="form"
       visible="true" enabled="true" val="add-to-cart" />
```

**Pass Criteria:** Submit button should show `enabled="true"` when all required fields complete

**Status: FAIL** - While button `enabled="true"` is visible in `find_elements`, there is no `<form_status>` section showing:
- All 6 completed fields with their selected values
- Form completion status (e.g., `ready_to_submit`)
- The expected structured summary is absent

---

## Issue #3: Click Result Feedback

**Problem:** After clicking, no clear confirmation of what changed.

### TC-3.1: Verify click success feedback

**Preconditions:**
- Browser on iPhone 17 page
- Storage options enabled

**Steps:**
1. Call `click` on 512GB storage option
2. Examine the response

**Expected Result:**
```xml
<action_result>
  <status>success</status>
  <action>click</action>
  <element_clicked eid="cf983dbff8d4" label="512GB" type="radio" />
  <state_change attribute="checked" from="false" to="true" />
  <side_effects>
    <enabled count="2">
      <element eid="60cdb551ce68" label="Select a smartphone" />
      <element eid="995d6b531909" label="No trade-in" />
    </enabled>
  </side_effects>
  <next_required field="trade-in" suggestion="Select trade-in preference" />
</action_result>
```

**Actual Result (Tested 2026-01-17):**
```xml
<state step="4" title="Buy iPhone 17 - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="false">
    <nodes added="2" removed="5" />
    <mutations>
      <status id="rd-770db2dd87" role="text">From</status>
      <status id="rd-5cb18ddd87" role="text">$999</status>
      <status id="rd-9b6a1e69c0" role="text">or</status>
      <status id="rd-6f7b30e91a" role="text">$41.62</status>
      <!-- ... many more text mutations about pricing ... -->
    </mutations>
  </diff>
  <observations>
    <during_action>
      <appeared significance="4">...</appeared>
      <disappeared significance="6">...</disappeared>
      <!-- Many appeared/disappeared elements -->
    </during_action>
  </observations>
  <region name="main">
    <rad id="e1f1e837396c" checked="true" focused="true" val="512gb">512GB...</rad>
    <rad id="7025a49d12aa" val="tradeIn">Select a smartphone...</rad>
    <rad id="362e05a22468" val="noTradeIn">No trade-in</rad>
  </region>
</state>
```

**Pass Criteria:** Click response should include structured action result with state changes and side effects

**Status: FAIL** - Response provides raw diff/mutations but lacks:
- `<action_result>` wrapper with `<status>success</status>`
- `<state_change attribute="checked" from="false" to="true" />`
- `<side_effects>` showing newly enabled trade-in options
- `<next_required>` suggestion for next step

---

### TC-3.2: Verify click on already-selected element

**Preconditions:**
- Browser on iPhone 17 page
- Black color already selected

**Steps:**
1. Call `click` on Black color option (already selected)
2. Examine the response

**Expected Result:**
```xml
<action_result>
  <status>no_change</status>
  <action>click</action>
  <element_clicked eid="11f0d284f957" label="Black" type="radio" />
  <note>Element was already selected</note>
</action_result>
```

**Actual Result (Tested 2026-01-17):**
```xml
<state step="5" title="Buy iPhone 17 - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="false">
    <nodes added="5" removed="0" />
    <mutations>
      <status id="rd-5a7d5ef67e" role="text">Previous gallery image</status>
      <status id="rd-622564436a" role="text">Next gallery image</status>
      <!-- Status text mutations, but nothing about the clicked element -->
    </mutations>
  </diff>
  <observations>
    <during_action>
      <appeared significance="6">
        <signals semantic="alert-role,aria-live" delayed="true" />
        <content tag="span" role="status"></content>
      </appeared>
    </during_action>
  </observations>
  <region name="main">
    <rad id="c40e8fe97453" checked="true" focused="true" val="black">Black</rad>
  </region>
</state>
```

**Pass Criteria:** Should indicate no change occurred when clicking already-selected element

**Status: FAIL** - Response is indistinguishable from a successful click. Missing:
- `<status>no_change</status>` indicator
- `<note>Element was already selected</note>` explanation

---

### TC-3.3: Verify click failure feedback on disabled element

**Preconditions:**
- Browser on iPhone 17 page
- Storage NOT selected yet
- Payment options are disabled

**Steps:**
1. Attempt to `click` on "Buy" payment option (disabled)
2. Examine the response

**Expected Result:**
```xml
<action_result>
  <status>failed</status>
  <action>click</action>
  <element_targeted eid="f9f258e63f3f" label="Buy" type="radio" />
  <error>Element is disabled</error>
  <reason>Requires prior selection: storage, trade-in</reason>
  <suggestion>
    <step order="1">Select storage option (256GB or 512GB)</step>
    <step order="2">Select trade-in preference</step>
    <step order="3">Then payment options will be enabled</step>
  </suggestion>
</action_result>
```

**Actual Result (Tested 2026-01-17):**
```xml
<state step="6" title="Buy iPhone 17 - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="false">
  </diff>
  <region name="main">
    <rad id="c40e8fe97453" checked="true" val="black">Black</rad>
  </region>
</state>
```

**Pass Criteria:** Click on disabled element should return clear error with remediation steps

**Status: FAIL** - Click silently fails with no error feedback. Missing:
- `<status>failed</status>` indicator
- `<error>Element is disabled</error>` message
- `<reason>` explaining required prior selections
- `<suggestion>` with remediation steps
- No indication that the click had no effect due to disabled state

---

## Issue #4: Stable Element References

**Problem:** Element IDs change between snapshots making tracking difficult.

### TC-4.1: Verify stable reference alongside volatile eid

**Preconditions:**
- Browser on iPhone 17 page

**Steps:**
1. Call `find_elements` with `kind: "radio"`, `label: "512GB"`
2. Check for stable reference attribute

**Expected Result:**
```xml
<match
  eid="cf983dbff8d4"
  stable_ref="iphone-config.storage.512gb"
  css="input[name='dimensionCapacity'][value='512gb']"
  xpath="//input[@value='512gb']"
  kind="radio"
  label="512GB..."
/>
```

**Actual Result (Current):**
```xml
<match eid="cf983dbff8d4" kind="radio" label="512GB..." val="512gb" />
```

**Pass Criteria:** Each element should have a `stable_ref` that persists across page updates

---

### TC-4.2: Verify stable reference persists after interaction

**Preconditions:**
- Browser on iPhone 17 page
- Note the stable_ref for 512GB option

**Steps:**
1. Call `find_elements`, note stable_ref for 512GB (e.g., `iphone-config.storage.512gb`)
2. Click on a different option (e.g., color)
3. Call `find_elements` again
4. Verify stable_ref for 512GB is unchanged

**Expected Result:**
- Step 1: `stable_ref="iphone-config.storage.512gb"`, `eid="cf983dbff8d4"`
- Step 4: `stable_ref="iphone-config.storage.512gb"`, `eid="NEW_ID_HERE"` (eid may change, stable_ref should not)

**Pass Criteria:** `stable_ref` should remain constant even when `eid` changes

---

### TC-4.3: Verify click by stable reference

**Preconditions:**
- Browser on iPhone 17 page
- stable_ref feature implemented

**Steps:**
1. Call `click` using stable_ref instead of eid:
   ```json
   { "stable_ref": "iphone-config.storage.512gb" }
   ```
2. Verify click succeeds

**Expected Result:**
```xml
<action_result>
  <status>success</status>
  <element_clicked stable_ref="iphone-config.storage.512gb" resolved_eid="cf983dbff8d4" />
  <state_change attribute="checked" from="false" to="true" />
</action_result>
```

**Pass Criteria:** Should be able to click elements using stable_ref

---

## Issue #5: Simplified Diff for State Changes

**Problem:** Current diffs are verbose with text mutations but lack actionable state info.

### TC-5.1: Verify state change summary in diff

**Preconditions:**
- Browser on iPhone 17 page
- Storage not yet selected

**Steps:**
1. Click on 512GB storage option
2. Examine the diff/state_changes in response

**Expected Result:**
```xml
<state_changes>
  <selections>
    <selected field="storage" value="512GB" eid="cf983dbff8d4" />
  </selections>
  <enabled_fields>
    <field name="trade-in" options="2" />
  </enabled_fields>
  <disabled_fields />
  <form_progress complete="2" remaining="4" next="trade-in" />
  <submit_button enabled="false" reason="4 required fields remaining" />
</state_changes>
```

**Actual Result (Tested 2026-01-17):**
```xml
<state step="4" title="Buy iPhone 17 - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="false">
    <nodes added="2" removed="5" />
    <mutations>
      <status id="rd-770db2dd87" role="text">From</status>
      <status id="rd-5cb18ddd87" role="text">$999</status>
      <status id="rd-9b6a1e69c0" role="text">or</status>
      <status id="rd-6f7b30e91a" role="text">$41.62</status>
      <status id="rd-0a3ff3b441" role="text">per month</status>
      <!-- ... many more text mutations about pricing ... -->
    </mutations>
  </diff>
  <observations>
    <during_action>
      <appeared significance="3">...</appeared>
      <disappeared significance="4">...</disappeared>
    </during_action>
  </observations>
  <region name="main">
    <rad id="e1f1e837396c" checked="true" focused="true" val="512gb">512GB...</rad>
    <rad id="7025a49d12aa" val="tradeIn">Select a smartphone...</rad>
    <rad id="362e05a22468" val="noTradeIn">No trade-in</rad>
  </region>
</state>
```

**Pass Criteria:** Diff should include high-level state_changes summary focused on form state

**Status: FAIL** - Response contains raw `<diff>` with text mutations (pricing). No `<state_changes>` section showing:
- `<selections>` for storage selection
- `<enabled_fields>` showing trade-in options became enabled
- `<form_progress>` showing completion status
- `<submit_button>` state

---

### TC-5.2: Verify enabled/disabled tracking in diff

**Preconditions:**
- Browser on iPhone 17 page
- Storage and trade-in selected

**Steps:**
1. Click on "Buy" payment option
2. Check state_changes for newly enabled carrier options

**Expected Result:**
```xml
<state_changes>
  <selections>
    <selected field="payment" value="Buy" eid="922d663c8b4a" />
  </selections>
  <enabled_fields>
    <field name="carrier" options="5">
      <option label="AT&T" eid="xxx" />
      <option label="Boost Mobile" eid="xxx" />
      <option label="T-Mobile" eid="xxx" />
      <option label="Verizon" eid="xxx" />
      <option label="Unlocked" eid="xxx" />
    </field>
  </enabled_fields>
  <form_progress complete="4" remaining="2" next="carrier" />
</state_changes>
```

**Actual Result (Tested 2026-01-17):**
```xml
<state step="6" title="Buy iPhone 17 - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="false">
    <nodes added="5" removed="5" />
    <mutations>
      <status id="rd-bdb3dc0694" role="text">From $999.00</status>
      <status id="rd-5a984fea4e" role="text">Footnote</status>
      <status id="rd-8c2f1490bb" role="text">‡</status>
      <status id="rd-1dd167f926" role="text">$999.00</status>
      <!-- ... many more pricing/footnote text mutations ... -->
    </mutations>
  </diff>
  <observations>
    <during_action>
      <appeared significance="3">...</appeared>
      <disappeared significance="4">...</disappeared>
    </during_action>
  </observations>
  <region name="main">
    <rad id="e5e40c439700" checked="true" focused="true" val="fullprice">Buy From $999.00...</rad>
    <rad id="c35932690256" val="ATT_IPHONE17">AT&T $999.00...</rad>
    <rad id="ea7205b48cba" val="BO•••NE">Boost Mobile $999.00...</rad>
    <rad id="1ab48a9f1c7f" val="TM•••HO">T-Mobile $999.00...</rad>
    <rad id="fd2bc12eb14c" val="VE•••HO">Verizon $999.00...</rad>
    <rad id="af13d09c8b15" val="UNLOCKED/US">Connect to any carrier later $1,029.00</rad>
  </region>
</state>
```

**Pass Criteria:** Should clearly show which fields became enabled after selection

**Status: FAIL** - Response shows text mutations in `<diff>`. Carrier options appearing is only visible in `<region>` content, not in a structured `<enabled_fields>` summary. Missing:
- `<selections>` showing payment = "Buy" was selected
- `<enabled_fields>` explicitly listing the 5 carrier options
- `<form_progress>` (4 complete, 2 remaining)

---

### TC-5.3: Verify submit button state in diff

**Preconditions:**
- Browser on iPhone 17 page
- All options selected except AppleCare

**Steps:**
1. Click on "No AppleCare coverage"
2. Check state_changes for submit button enablement

**Expected Result:**
```xml
<state_changes>
  <selections>
    <selected field="applecare" value="No AppleCare" eid="721d83c48224" />
  </selections>
  <enabled_fields>
    <submit_button label="Add to Bag" eid="18eb7ccd357c" />
  </enabled_fields>
  <form_progress complete="6" remaining="0" status="ready_to_submit" />
  <submit_button enabled="true" label="Add to Bag" eid="18eb7ccd357c" />
</state_changes>
```

**Actual Result (Tested 2026-01-17):**
```xml
<state step="8" title="Buy iPhone 17 512GB Black - Apple" url="...">
  <meta view="1280x720" scroll="0,0" layer="main" />
  <diff type="mutation" empty="false">
    <nodes added="0" removed="1" />
    <mutations>
      <status id="rd-296f546b4b" role="text">AppleCare+ with Theft and Loss</status>
      <status id="rd-9564ace8e2" role="text">Cover this product only</status>
      <status id="rd-35a5d8ea34" role="text">$11.99</status>
      <status id="rd-c74d448f99" role="text">per month</status>
      <status id="rd-9223e7c76e" role="text">No AppleCare coverage</status>
      <status id="rd-2e624d2f37" role="text">Add to Bag</status>
      <!-- ... AppleCare pricing text mutations ... -->
    </mutations>
  </diff>
  <observations>
    <during_action>
      <appeared significance="3">...</appeared>
    </during_action>
  </observations>
  <region name="main">
    <rad id="a5e5a0b7c633" checked="true" focused="true">No AppleCare coverage</rad>
  </region>
  <region name="form">
    <btn id="31f426071430" val="add-to-cart">Add to Bag</btn>
    <!-- Note: enabled="false" is ABSENT, indicating button is now enabled -->
  </region>
</state>
```

**Pass Criteria:** Submit button enablement should be prominently shown in state_changes

**Status: FAIL** - Submit button enablement only discoverable by comparing `<region>` content:
- **Before:** `<btn id="31f426071430" enabled="false" val="add-to-cart">Add to Bag</btn>`
- **After:** `<btn id="31f426071430" val="add-to-cart">Add to Bag</btn>` (no `enabled="false"`)

Missing:
- `<selections>` showing applecare = "No AppleCare"
- `<submit_button enabled="true" label="Add to Bag">` explicit state
- `<form_progress complete="6" remaining="0" status="ready_to_submit" />`

---

## Issue #6: Warnings for Disabled Element Clicks

**Problem:** Clicking disabled elements silently fails with no guidance.

### TC-6.1: Verify warning when clicking disabled element

**Preconditions:**
- Browser on iPhone 17 page
- Storage NOT selected
- Payment options are disabled

**Steps:**
1. Attempt to click "Buy" payment option (disabled)
2. Examine response for warning

**Expected Result:**
```xml
<warning type="disabled_element">
  <element eid="f9f258e63f3f" label="Buy" type="radio" />
  <message>Cannot click disabled element</message>
  <reason>This field requires prior selections</reason>
  <dependencies>
    <dependency field="storage" status="not_selected" required="true" />
    <dependency field="trade-in" status="disabled" required="true" />
  </dependencies>
  <suggestion>
    First select a storage option, then trade-in preference. Payment options will then become available.
  </suggestion>
  <next_action>
    <click eid="b492c4dc6354" label="256GB" /> <!-- or -->
    <click eid="cf983dbff8d4" label="512GB" />
  </next_action>
</warning>
```

**Actual Result (Current):** No warning, action appears to complete but nothing changes

**Pass Criteria:** Clear warning with dependencies and suggested next action

---

### TC-6.2: Verify warning includes full dependency chain

**Preconditions:**
- Browser on iPhone 17 page
- Only color selected
- AppleCare options are disabled (deep in dependency chain)

**Steps:**
1. Attempt to click "No AppleCare coverage" (disabled)
2. Examine warning for full dependency chain

**Expected Result:**
```xml
<warning type="disabled_element">
  <element eid="721d83c48224" label="No AppleCare coverage" type="radio" />
  <message>Cannot click disabled element</message>
  <dependency_chain>
    <step order="1" field="storage" status="not_selected" action_required="true" />
    <step order="2" field="trade-in" status="disabled" depends_on="storage" />
    <step order="3" field="payment" status="disabled" depends_on="trade-in" />
    <step order="4" field="carrier" status="disabled" depends_on="payment" />
    <step order="5" field="applecare" status="disabled" depends_on="carrier" />
  </dependency_chain>
  <immediate_action>Select storage option first</immediate_action>
</warning>
```

**Pass Criteria:** Warning should show full dependency chain, not just immediate dependency

---

### TC-6.3: Verify no warning when clicking enabled element

**Preconditions:**
- Browser on iPhone 17 page
- Storage options are enabled

**Steps:**
1. Click 512GB storage option (enabled)
2. Verify no warning in response

**Expected Result:**
```xml
<action_result>
  <status>success</status>
  <!-- No warning element present -->
  <element_clicked eid="cf983dbff8d4" label="512GB" />
  <state_change attribute="checked" from="false" to="true" />
</action_result>
```

**Pass Criteria:** No warning should appear for successful clicks on enabled elements

---

## Issue #7: Form Detection Tool Enhancement

**Problem:** `form_detect` doesn't reveal dependency chains or form flow.

### TC-7.1: Verify form_detect returns dependency chain

**Preconditions:**
- Browser on iPhone 17 page

**Steps:**
1. Call `form_detect` on the page
2. Examine response for dependency information

**Expected Result:**
```xml
<form_analysis id="iphone-config" type="multi-step">
  <dependency_chain>
    <step order="1" field="color" type="radio" options="5" required="true" />
    <step order="2" field="storage" type="radio" options="2" required="true" />
    <step order="3" field="trade-in" type="radio" options="2" required="true" depends_on="storage" />
    <step order="4" field="payment" type="radio" options="3" required="true" depends_on="trade-in" />
    <step order="5" field="carrier" type="radio" options="5" required="true" depends_on="payment" />
    <step order="6" field="applecare" type="radio" options="3" required="true" depends_on="carrier" />
  </dependency_chain>
  <submit_button label="Add to Bag" eid="18eb7ccd357c" enabled_when="all_required_complete" />
  <form_type>sequential_selection</form_type>
</form_analysis>
```

**Actual Result (Current):**
```xml
<form_detect returns flat list of fields without dependency info>
```

**Pass Criteria:** form_detect should return dependency chain with order and depends_on relationships

---

### TC-7.2: Verify form_detect shows current step

**Preconditions:**
- Browser on iPhone 17 page
- Color and storage selected, on trade-in step

**Steps:**
1. Call `form_detect`
2. Check for current step indicator

**Expected Result:**
```xml
<form_analysis id="iphone-config">
  <current_state>
    <completed_steps>
      <step field="color" value="Black" />
      <step field="storage" value="512GB" />
    </completed_steps>
    <current_step field="trade-in" status="awaiting_selection">
      <options>
        <option eid="60cdb551ce68" label="Select a smartphone" />
        <option eid="995d6b531909" label="No trade-in" recommended="true" />
      </options>
    </current_step>
    <pending_steps>
      <step field="payment" enabled="false" />
      <step field="carrier" enabled="false" />
      <step field="applecare" enabled="false" />
    </pending_steps>
  </current_state>
  <progress percent="33" completed="2" total="6" />
</form_analysis>
```

**Pass Criteria:** form_detect should indicate current step and progress

---

### TC-7.3: Verify form_detect identifies blocking fields

**Preconditions:**
- Browser on iPhone 17 page
- Some fields selected, some missing

**Steps:**
1. Select color, storage, trade-in, payment (skip to carrier without selecting)
2. Call `form_detect`
3. Check for blocking field identification

**Expected Result:**
```xml
<form_analysis id="iphone-config">
  <blocking_fields>
    <field name="carrier" status="required_not_selected" message="Select a carrier or Unlocked option">
      <options>
        <option eid="xxx" label="AT&T" />
        <option eid="xxx" label="Unlocked" recommended="true" />
      </options>
    </field>
  </blocking_fields>
  <submit_button enabled="false" blocked_by="carrier,applecare" />
</form_analysis>
```

**Pass Criteria:** form_detect should clearly identify which fields are blocking form submission

---

### TC-7.4: Verify form_detect with scope parameter

**Preconditions:**
- Browser on page with multiple forms

**Steps:**
1. Call `form_detect` with scope limited to iPhone config form:
   ```json
   { "scope": { "css": "form#iphone-configuration" } }
   ```
2. Verify only target form is analyzed

**Expected Result:**
```xml
<form_analysis id="iphone-config" scope_matched="form#iphone-configuration">
  <!-- Only iPhone config form details, not other page forms -->
</form_analysis>
```

**Pass Criteria:** form_detect should respect scope parameter and only analyze specified form

---

## Test Execution Summary Template

| Test Case | Description | Status | Notes |
|-----------|-------------|--------|-------|
| TC-1.1 | enabled/disabled full words | PASS | Uses `enabled="true"` / `enabled="false"` in both `find_elements` and `get_node_details` |
| TC-1.2 | checked state full words | PASS | Uses `checked="true"` / `checked="false"` in both `find_elements` and `get_node_details` |
| TC-1.3 | required field indication | PARTIAL | `required="true"` available in `get_node_details` only, not in `find_elements` output |
| TC-2.1 | form status after load | FAIL | No `<form_status>` section in `capture_snapshot` or `find_elements`. No visibility into required fields, dependencies, or blocking status |
| TC-2.2 | form status after selection | FAIL | No form status updates after selections. Expected `<form_status>` with completed fields and newly enabled fields is absent |
| TC-2.3 | submit button tracking | FAIL | Button `enabled="true"` visible in `find_elements`, but no form-level summary showing completion status or field values |
| TC-3.1 | click success feedback | FAIL | Returns raw diff/mutations. No `<action_result>` with `<status>success</status>`, `<state_change>`, `<side_effects>`, or `<next_required>` |
| TC-3.2 | click already-selected | FAIL | Response indistinguishable from successful click. No `<status>no_change</status>` or `<note>Element was already selected</note>` |
| TC-3.3 | click disabled feedback | FAIL | Click silently fails. No error, no warning, no dependency chain, no remediation suggestion |
| TC-4.1 | stable reference present | | |
| TC-4.2 | stable ref persists | | |
| TC-4.3 | click by stable ref | | |
| TC-5.1 | state change summary | FAIL | Response contains raw `<diff>` with text mutations. No `<state_changes>` section with selections, enabled_fields, or form_progress |
| TC-5.2 | enabled/disabled in diff | FAIL | Carrier options only visible in `<region>` content, not in structured `<enabled_fields>` summary |
| TC-5.3 | submit button in diff | FAIL | Button enablement only discoverable by comparing `<region>` (absence of `enabled="false"`). No explicit `<submit_button enabled="true">` |
| TC-6.1 | disabled click warning | | |
| TC-6.2 | full dependency chain | | |
| TC-6.3 | no warning on enabled | | |
| TC-7.1 | dependency chain | | |
| TC-7.2 | current step indicator | | |
| TC-7.3 | blocking fields | | |
| TC-7.4 | scope parameter | | |

---

## Appendix: Test Data

### Apple Store iPhone 17 Configuration Options

| Field | Options | Default |
|-------|---------|---------|
| Color | Lavender, Sage, Mist Blue, White, Black | None |
| Storage | 256GB, 512GB | None |
| Trade-in | Select smartphone, No trade-in | None |
| Payment | Buy, Finance, Upgrade Program | None |
| Carrier | AT&T, Boost, T-Mobile, Verizon, Unlocked | None |
| AppleCare | AppleCare+, AppleCare One, No AppleCare | None |

### Dependency Chain

```
color (always enabled)
  └── storage (always enabled)
        └── trade-in (enabled after storage)
              └── payment (enabled after trade-in)
                    └── carrier (enabled after payment)
                          └── applecare (enabled after carrier)
                                └── Add to Bag (enabled after applecare)
```
