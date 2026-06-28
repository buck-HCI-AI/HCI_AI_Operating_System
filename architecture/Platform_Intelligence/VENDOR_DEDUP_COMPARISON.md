# Vendor Record Analysis — Multi-Contact & Duplicate Review
**Date:** 2026-06-28 | **Groups:** 67 companies | **Records:** 186

## Analysis Finding
Most 'duplicates' are **multi-contact companies** — one vendor row per contact person at the same company.
The data model stores contacts inside the vendors table. Recommended fix: keep highest-bid-count row as primary; consolidate contact info into that row's notes field; deactivate extras.

| Type | Companies | Records | Action |
|---|---|---|---|
| Multi-contact (different people, same company) | 67 | 186 | Keep primary, merge contacts to notes |
| True duplicates (same person, multiple entries) | 0 | 0 | Buck selects canonical, deactivate rest |

---

## Multi-Contact Companies (different people, same firm)
*Action: Keep the row with highest bid_count as primary. Add other contacts to notes. Deactivate extras.*

### Sunny Oasis Holdings Limited (Melco) (10 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 380 | Graeme Thompson | graemealexanderthompson@melco-resorts.com | — | — | 0 |  ✅ (primary) |
| 381 | Kanaan Nader | kanaannader@melco-resorts.com | — | — | 0 |  |
| 382 | Jack Fung | jackfung@melco-resorts.com | — | — | 0 |  |
| 383 | Vincent Sit | vincentsit@melco-resorts.com | — | — | 0 |  |
| 384 | Alex Ip | alexip@melco-resorts.com | — | — | 0 |  |
| 385 | Alan Evans | alanevans@melco-resorts.com | — | — | 0 |  |
| 386 | John Sit | johnsit@melco-resorts.com | — | — | 0 |  |
| 387 | Guilielmus Robberecht | guilielmusrobberecht@melco-resorts.com | — | — | 0 |  |
| 388 | Matthew Chun | matthewchun@melco-resorts.com | — | — | 0 |  |
| 389 | Jocelyn Suniga | jocelynsuniga@melco-resorts.com | — | — | 0 |  |

### Ajax Mechanical Services (6 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 171 | Jennifer Wagner | billing@ajaxmechanical.com | (970) 984-0579 | Mechanical | 0 |  ✅ (primary) |
| 257 | Janice Sebald | janice@ajaxmechanical.com | (970) 984-0579 | Mechanical | 0 |  |
| 304 | John Stone | dispatch@ajaxmechanical.com | (970) 984-0579 | Mechanical | 0 |  |
| 317 | Janice Sebald | jsebald.ams@gmail.com | (970) 984-0579 | Mechanical | 0 |  |
| 335 | John- | ajaxmechanicalservices@live.com | (970) 618-7832 | Mechanical | 0 |  |
| 348 | Mike Vogel | — | (970) 618-2393 | Mechanical | 0 |  |

### City of Aspen (6 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 54 | Justin Forman | justin.forman@cityofaspen.com | (970) 319-2210 | — | 0 |  ✅ (primary) |
| 94 | Jim Pomeroy | jim.pomeroy@cityofaspen.com | (970) 319-2565 | — | 0 |  |
| 95 | Trish Aragon | trish.aragon@cityofaspen.com | (970) 429-2785 | — | 0 |  |
| 100 | Bob Rugile | bob.rugile@cityofaspen.com | (970) 920-5080 | — | 0 |  |
| 227 | Justin Hahn | justin.hahn@cityofaspen.com | (970) 429-2784 | — | 0 |  |
| 247 | Dennis Murray | denis.murray@cityofaspen.com | (970) 309-6283 | — | 0 |  |

### Custom Structural Steel (6 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 270 | Bruce Bell | bruce@cssteelinc.com | (970) 618-3929 | Structural Steel | 0 |  ✅ (primary) |
| 295 | Bruce | — | — | Structural Steel | 0 |  |
| 325 | Dennis Clancy | dennis@cs-steelinc.com | (970) 625-0345 | Structural Steel | 0 |  |
| 326 | Bruce Bell | bruce@pinestoneco.com | (970) 618-3929 | Structural Steel | 0 |  |
| 342 | Jim Suehring | jim@cs-steelinc.com | (970) 625-0345 | Structural Steel | 0 |  |
| 356 | Joe Wilson | accounting@cs-steelinc.com | (970) 625-0345 | Structural Steel | 0 |  |

### Pitkin County Community Development (5 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 113 | Bonnie Shiles | bonnie.shiles@pitkincounty.com | (970) 920-5109 | — | 0 |  ✅ (primary) |
| 147 | Mike Kraemer | — | (970) 309-2036 | — | 0 |  |
| 163 | Beth Hansen | beth.hansen@pitkincounty.com | (970) 920-5524 | — | 0 |  |
| 185 | Kristi Long | kristi.long@pitkincounty.com | (970) 920-5092 | — | 0 |  |
| 280 | Suzanne Wolff | suzanne.wolff@pitkincounty.com | (970) 920-5093 | — | 0 |  |

### Savage Excavation (5 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 80 | Jennifer | jennifer@savageexco.com | — | Sitework | 0 |  ✅ (primary) |
| 93 | Sophie Schlumberger | sophie@savagexco.com | (970) 963-3424 | Sitework | 0 |  |
| 143 | Ray Simpson | ray@savagexco.com | (970) 379-8575 | Sitework | 0 |  |
| 331 | Ray Simpson | savageexcavation@sopris.net | (970) 379-8575 | Sitework | 0 |  |
| 339 | Carter Schlumberger Ray Simpson | office@savagexco.com | (970) 379-8575 | Sitework | 0 |  |

### Castlewood Doors (4 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 62 | Tiffany Rowe | trowe@castlewooddoors.com | (970) 901-7613 | Doors & Hardware | 0 |  ✅ (primary) |
| 208 | Joel Algra | jjosephish@aol.com | (970) 471-5679 | Doors & Hardware | 0 |  |
| 216 | Juan Molina | juan@castlewooddoors.com | (970) 948-6889 | Doors & Hardware | 0 |  |
| 340 | — | info@casaverdepainy.com | (303) 777-0517 | Doors & Hardware | 0 |  |

### Kumar & Associates, Inc. (4 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 104 | Steve Pawlak | spawlak@kumarusa.com | (970) 945-7988 | — | 0 |  ✅ (primary) |
| 299 | Brenda Johnson | bjohnson@kumarusa.com | (303) 742-9700 | — | 0 |  |
| 316 | Lena Fowlkes | lfowlkes@kumarusa.com | (970) 945-7988 | — | 0 |  |
| 359 | — | kadenver@kumarusa.com | (303) 742-9700 | — | 0 |  |

### R & H Mechanical (4 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 240 | Daniel Angeloro | dan@randhmechanical.com | (970) 309-8711 | Mechanical | 0 |  ✅ (primary) |
| 318 | — | info@randhmechanical.com | (970) 328-2699 | Mechanical | 0 |  |
| 328 | Dan Angeloro | daniela@randhmechanical.com | (970) 328-2699 | Mechanical | 0 |  |
| 358 | — | accounting@cccgws.com | (970) 945-2326 | Mechanical | 0 |  |

### Rader Engineering, Inc (4 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 290 | Patti Rader | pattir@raderengineering.com | (970) 845-7910 | — | 0 |  ✅ (primary) |
| 321 | Drew Rader | — | (970) 845-7910 | — | 0 |  |
| 330 | Jeff Herschel | jeffh@raderengineering.com | (602) 421-9579 | — | 0 |  |
| 377 | Drew Kitchell | drew@mckinleysales.com | (970) 379-7777 | — | 0 |  |

### Architectural Windows & Doors (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 27 | Michael Dollahan | miked@awd.cc | (970) 379-2933 | Glazing | 0 |  ✅ (primary) |
| 319 | Brad Biddlestone | bradb@awd.cc | (970) 618-0191 | Glazing | 0 |  |
| 324 | — | ar@awd.cc | (970) 928-9314 | Glazing | 0 |  |

### Aspen Insulation Company (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 12 | Brittney Hellinger | brittney@aspeninsulation.com | (970) 945-5088 | Insulation | 0 |  ✅ (primary) |
| 205 | Bobby McLelland | bobby@aspeninsulation.com | (970) 945-5088 | Insulation | 0 |  |
| 301 | Tom | tom@aspeninsulation.com | (970) 319-8639 | Insulation | 0 |  |

### Aspen Property Management (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 90 | Matt Haag Apm | matt@aspenpropertymngt.com | (970) 618-8155 | — | 0 |  ✅ (primary) |
| 99 | Leslie Apm | lesliecitron1@gmail.com | (917) 885-0264 | — | 0 |  |
| 279 | Peter | peter@aspenpropertymngt.com | (970) 618-6856 | — | 0 |  |

### Clear Vu Window Tinting (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 289 | Brian | clear-vu@comcast.net | (970) 927-0274 | Glazing | 0 |  ✅ (primary) |
| 349 | John Hembel | — | (970) 927-0274 | Glazing | 0 |  |
| 357 | Brian Westvedt | clearvuwindowtint@gmail.com | (970) 379-2873 | Glazing | 0 |  |

### Dynamic Fenestration (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 5 | Aaron Wu | aaronwu@dynamicfenestration.com | (800) 661-9111 | Glazing | 0 |  ✅ (primary) |
| 29 | Eric Celko | eric@dynamicfenestration.com | (604) 864-8200 | Glazing | 0 |  |
| 296 | — | millad@dynamicfenestration.com | — | Glazing | 0 |  |

### Epic Custom Glass, LLC (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 8 | Brad Quinty | bradquinty@icloud.com | (970) 366-2556 | Glazing | 0 |  ✅ (primary) |
| 9 | Annette Dismore | annette@epiccustomglass.com | (970) 947-9456 | Glazing | 0 |  |
| 341 | — | office@epiccustomglass.com | (970) 947-9456 | Glazing | 0 |  |

### Green Electrical Solutions LLC (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 26 | Jay | jay@greenelectrical.solutions | (970) 379-3348 | Electrical | 0 |  ✅ (primary) |
| 320 | — | rachel@greenelectrical.solutions | — | Electrical | 0 |  |
| 364 | — | billing@greenelectrical.solutions | (970) 379-3348 | Electrical | 0 |  |

### High Country Engineering , Inc. (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 69 | Roger Neal | rneal@hceng.com | (970) 945-2555 | — | 0 |  ✅ (primary) |
| 108 | Becky Hale | frontdesk@hceng.com | (970) 945-2555 | — | 0 |  |
| 310 | Romeo Baylosis | rbaylosis@hceng.com | (970) 471-1103 | — | 0 |  |

### Integrity Fire Safety Services, LLC (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 28 | Spencer Boothe | spencer.boothe@integrityfiresafetyservices.com | (303) 557-1820 | Mechanical | 0 |  ✅ (primary) |
| 38 | Rebecca Boothe | rebecca.boothe@integrityfiresafetyservices.com | (303) 557-1820 | Mechanical | 0 |  |
| 285 | — | office@flameoutfire.net | — | Mechanical | 0 |  |

### Morning Star Elevator (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 165 | Sean Paxson | sean@mselevator.com | (970) 481-0325 | Elevator | 0 |  ✅ (primary) |
| 268 | Cheryl Niles | cheryl@mselevator.com | (719) 635-7960 | Elevator | 0 |  |
| 368 | — | richard@mselevator.com | (719) 635-7960 | Elevator | 0 |  |

### NanoLumens (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 183 | Eric Seigler | eseigler@nanolumens.com | (404) 964-0112 | Equipment | 0 |  ✅ (primary) |
| 206 | Randy Bortles | randybortles@nanolumens.com | (678) 488-0619 | Equipment | 0 |  |
| 254 | Dan Rossborough | drossborough@nanolumens.com | (678) 333-3783 | Equipment | 0 |  |

### ProGuard (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 112 | Dave Divine | david.divine@att.net | (970) 319-2405 | — | 0 |  ✅ (primary) |
| 327 | Carl Proguard | cheryl@proguardprotection.com | (970) 927-2026 | — | 0 |  |
| 365 | Bonnie Guard | — | (970) 927-2026 | — | 0 |  |

### ProGuard Protection Services Inc (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 30 | Cheryl | cheryl@progaurdprotection.com | (970) 927-2026 | Electrical | 0 |  ✅ (primary) |
| 34 | David Divine | david@proguardprotection.com | (916) 580-5280 | Electrical | 0 |  |
| 363 | Genny Hardenbrook | genny@proguardprotection.com | (970) 927-2026 | Electrical | 0 |  |

### Probuild dba Builders FirstSource (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 336 | — | colorado.credit@bldr.com | (970) 945-5464 | General Contractor | 1 |  ✅ (primary) |
| 337 | Brian probuild | — | (970) 925-4262 | General Contractor | 0 |  |
| 345 | Andrew Underhill | brian.fremont@probuild.com | (970) 925-4262 | General Contractor | 0 |  |

### SnowCap Decorative Hardware LLC (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 182 | Kelly Korth | kelly@snowcapdh.com | (970) 872-3889 | Doors & Hardware | 0 |  ✅ (primary) |
| 215 | Dani Galley | dani@snowcapdh.com | (970) 872-3878 | Doors & Hardware | 0 |  |
| 361 | Kelly | — | (970) 872-3889 | Doors & Hardware | 0 |  |

### Sopris Mechanical (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 144 | Brandon Renck | — | (970) 618-9378 | Mechanical | 0 |  ✅ (primary) |
| 347 | Brandon Renck | — | (970) 618-9378 | Mechanical | 0 |  |
| 360 | Jason Mak | jason@soprismechanical.com | (970) 618-0282 | Mechanical | 0 |  |

### The Fireplace Company (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 201 | Christine Company | — | (970) 963-3598 | Specialties | 0 |  ✅ (primary) |
| 355 | Christine Company | — | (970) 963-3598 | Specialties | 0 |  |
| 370 | Al Blick | al@thefpco.com | (970) 963-3598 | Specialties | 0 |  |

### Valley Lumber (3 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 85 | Paul Gonzales | vlpaulg@gmail.com | (970) 927-3146 | Rough Carpentry | 0 |  ✅ (primary) |
| 303 | — | todd@valleylumber.com | (970) 927-3146 | Rough Carpentry | 0 |  |
| 308 | Paul Gonzales | vpaulg@gmail.com | (970) 927-3146 | Rough Carpentry | 0 |  |

### 2H Mechanical LLC (2 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 17 | Luke Glowacki | lukeg@2hmech.com | (970) 433-8521 | Mechanical | 0 |  ✅ (primary) |
| 19 | Danny Ray | danny@2hmech.com | (970) 779-4560 | Mechanical | 0 |  |

### AAA Mountain Waterproofing LLC (2 contacts)
| ID | Contact | Email | Phone | Trade | Bids | KEEP? |
|---|---|---|---|---|---|---|
| 25 | Alec Bowler | estimating@aaawpg.com | (970) 978-1962 | Waterproofing | 0 |  ✅ (primary) |
| 338 | Dawn McKissack | dawn@aaawpg.com | (970) 625-9257 | Waterproofing | 0 |  |

