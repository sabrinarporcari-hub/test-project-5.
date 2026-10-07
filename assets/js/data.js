/*
  Gallery records. Every value comes from the presentation
  (Al_Maryah_Island_AI_Image_Library_Proposal_13.pptx); slide numbers in comments.
  A field set to null renders as "Not yet recorded". Fill it in here when the record exists.
*/
(function () {
  const ROUTE_PEOPLE = {
    v: 'Higgsfield Soul · FLUX · Nano Banana Pro',
    note: 'People & lifestyle route on Omni (slide 90). Final model and version per frame not yet recorded.'
  };
  const STYLE = 'Natural skin, fine grain. Directed like a shoot, from the brand book (Photography 6.01).';
  const grade = (echo) => echo
    ? 'One library colour grade (LUT). Colour echo: ' + echo + '.'
    : 'One library colour grade (LUT).';

  const ECHO = {
    sky: { name: 'sky & slate blue', ink: '#9acaeb' },
    oxford: { name: 'Oxford blue', ink: '#86aed0' },
    vermilion: { name: 'vermilion', ink: '#ef7a5f' },
    gold: { name: 'sky to gold', ink: '#e6bb72' },
    bronze: { name: 'bronze', ink: '#d2a89b' },
    bronzeOxford: { name: 'bronze & Oxford', ink: '#c9aaa3' }
  };

  window.AMI_GALLERY = [
    {
      // slides 19, 26, 85
      id: 'w01-recovery', src: 'assets/img/gallery/w01-recovery-moment.jpg', w: 1539, h: 1216,
      world: 'W01', worldName: 'Wellness & Leisure', pillar: 'Exceptional Living', hour: '07:00', h24: 7,
      title: 'Recovery moment', channel: 'Key visual', audience: 'Residents', echo: ECHO.sky,
      alt: 'A woman in workout clothes rests on a pool deck at sunrise, towel round her neck and a water bottle in hand, with the island towers reflected in the water behind her.',
      fields: {
        prompt: null,
        model: ROUTE_PEOPLE,
        camera: null,
        lens: null,
        focal: '50mm (the read)',
        aperture: null,
        light: 'Soft sunrise',
        time: '07:00',
        location: 'Pool deck',
        cast: 'The resident (character sheet)',
        wardrobe: null,
        composition: 'Medium',
        style: STYLE,
        colour: grade(ECHO.sky.name),
        params: '3:2 master. Use: social, CRM (42-shot matrix).'
      }
    },
    {
      // slide 25
      id: 'w01-movement', src: 'assets/img/gallery/w01-movement.jpg', w: 600, h: 900,
      world: 'W01', worldName: 'Wellness & Leisure', pillar: 'Exceptional Living', hour: '07:00', h24: 7.35,
      title: 'Movement', channel: 'Out of home · Adshel', audience: null, echo: ECHO.sky,
      alt: 'A woman runs along the waterfront promenade in early morning haze, palms on her left and towers in the distance.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null, focal: null, aperture: null,
        light: 'Sunrise haze', time: '07:00', location: 'Promenade run',
        cast: 'The resident (character sheet)', wardrobe: null, composition: null,
        style: STYLE, colour: grade(null), params: '2:3 master, adshel in the ad system.'
      }
    },
    {
      // slides 27, 28, 85
      id: 'w02-arrival', src: 'assets/img/gallery/w02-executive-arrival.jpg', w: 1539, h: 1216,
      world: 'W02', worldName: 'Business & Professional', pillar: 'Exceptional Commerce', hour: '09:00', h24: 9,
      title: 'Executive arrival', channel: 'Key visual', audience: 'Professionals, investors', echo: ECHO.oxford,
      alt: 'In a glass-walled tower lobby, a man in a navy suit shakes hands with an Emirati executive in a white kandura and ghutra while colleagues walk past.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null,
        focal: '24mm (the read)', aperture: null, light: 'Glass daylight', time: '09:00',
        location: 'Tower lobby', cast: 'The professional (character sheet)', wardrobe: null,
        composition: 'Wide', style: STYLE, colour: grade(ECHO.oxford.name),
        params: '3:2 master. Use: website hero (42-shot matrix).'
      }
    },
    {
      // slides 35, 38
      id: 'w03-fragrance', src: 'assets/img/gallery/w03-fragrance-moment.jpg', w: 1539, h: 1216,
      world: 'W03', worldName: 'Shopping & Retail', pillar: 'Exceptional Living', hour: '13:00', h24: 13,
      title: 'Fragrance moment', channel: 'Key visual', audience: 'Visitors, tourists', echo: ECHO.vermilion,
      alt: 'Two women in shaylas test perfume at a fragrance boutique counter; one smells a blotter strip while the other smiles, with red roses in the foreground.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null,
        focal: '85mm (the read)', aperture: null, light: 'Warm boutique', time: '13:00',
        location: 'Fragrance boutique', cast: 'GCC visitors (character sheet)', wardrobe: null,
        composition: null, style: STYLE, colour: grade(ECHO.vermilion.name), params: '3:2 master.'
      }
    },
    {
      // slides 43, 49, 85
      id: 'w04-walk', src: 'assets/img/gallery/w04-golden-hour-walk.jpg', w: 1539, h: 1216,
      world: 'W04', worldName: 'Waterfront & Outdoor', pillar: 'Exceptional Living', hour: '17:30', h24: 17.5,
      title: 'Golden hour walk', channel: 'Key visual', audience: 'Residents, visitors', echo: ECHO.gold,
      alt: 'A couple in linen walk and laugh along the promenade at golden hour, backlit by a low sun, with palms and towers behind them.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null,
        focal: '35mm (the read)', aperture: null, light: 'Low backlight', time: '17:30',
        location: 'Promenade', cast: 'Couple, 30s', wardrobe: null,
        composition: 'Medium-wide', style: STYLE, colour: grade(ECHO.gold.name),
        params: '3:2 master. Use: OOH, print (42-shot matrix).'
      }
    },
    {
      // slides 79, 87, 92, 100, 101: the one frame with a full record
      id: 'w04-promenade', src: 'assets/img/gallery/w04-golden-hour-promenade.jpg', w: 1672, h: 941,
      world: 'W04', worldName: 'Waterfront & Outdoor', pillar: 'Exceptional Living', hour: '17:30', h24: 17.85,
      title: 'Golden hour promenade', channel: 'Master', audience: null, echo: ECHO.gold,
      file: 'AMI_W04_GoldenHourPromenade_3x2_Master_v01.tif',
      alt: 'An Emirati couple, he in a white kandura and ghutra, she in a black abaya and shayla, walk along the waterfront promenade at golden hour with the sun low between the towers.',
      fields: {
        prompt: 'Golden hour on the Al Maryah Island waterfront promenade, 5:30 pm. A couple in their 30s, mid-conversation, walking unhurried. Palms and towers across the water. 35mm, eye level, f/4. Low sun, backlit, long shadows. Unhurried, warm. Linen, understated. Modest, contemporary UAE. Natural skin, fine grain. 3:2 master.',
        model: { v: '[Model · version]', note: 'Left open in the sample prompt record (slide 101). Route: Higgsfield Soul · FLUX · Nano Banana Pro.' },
        camera: null,
        lens: null,
        focal: '35mm, contextual read',
        aperture: 'f/4',
        light: 'Low sun, backlit, long shadows',
        time: '17:30, golden hour',
        location: 'Waterfront promenade: palms, towers. Matched to the recce reference.',
        cast: 'Couple, 30s. Mid-stride, mid-laugh.',
        wardrobe: 'Linen, understated. Modest, contemporary UAE.',
        composition: 'Medium-wide, eye level',
        style: 'Natural skin, fine grain. Mood: unhurried, warm.',
        colour: grade(ECHO.gold.name),
        params: 'Seed not yet recorded · 3:2 master. References: cast sheet, wardrobe brief, W04 promenade. Excluded: text, signage, logos, waxy skin, distorted hands. Edits: inpainting (hands, fabric), retouch (signage). Rounds R1–R4.'
      }
    },
    {
      // slide 46
      id: 'w04-family', src: 'assets/img/gallery/w04-family-outdoors.jpg', w: 600, h: 900,
      world: 'W04', worldName: 'Waterfront & Outdoor', pillar: 'Exceptional Living', hour: '17:30', h24: 18.2,
      title: 'Family outdoors', channel: 'Out of home · Adshel', audience: null, echo: ECHO.gold,
      alt: 'A mother in an abaya walks the promenade at golden hour holding hands with her small daughter, towers and palms behind them.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null, focal: null, aperture: null,
        light: 'Golden hour', time: '17:30', location: 'Promenade', cast: 'Mother & daughter',
        wardrobe: null, composition: null, style: STYLE, colour: grade(null),
        params: '2:3 master, adshel in the ad system.'
      }
    },
    {
      // slides 51, 53
      id: 'w05-dinner', src: 'assets/img/gallery/w05-dinner-with-friends.jpg', w: 1539, h: 1216,
      world: 'W05', worldName: 'Dining & Hospitality', pillar: 'Exceptional Hospitality', hour: '20:00', h24: 20,
      title: 'Dinner with friends', channel: 'Key visual', audience: 'Visitors, tourists', echo: ECHO.bronze,
      alt: 'Three women share dishes by candlelight at a waterfront terrace table at night, laughing, with the lit skyline across the water.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null,
        focal: '35mm, table (the read)', aperture: null, light: 'Candlelight', time: '20:00',
        location: 'Waterfront terrace', cast: 'The friends (character sheet)', wardrobe: null,
        composition: null, style: STYLE, colour: grade(ECHO.bronze.name), params: '3:2 master.'
      }
    },
    {
      // slide 56
      id: 'w05-couple', src: 'assets/img/gallery/w05-couple-dining.jpg', w: 600, h: 900,
      world: 'W05', worldName: 'Dining & Hospitality', pillar: 'Exceptional Hospitality', hour: '20:00', h24: 20.35,
      title: 'Couple dining', channel: 'Out of home · Adshel', audience: null, echo: ECHO.bronze,
      alt: 'A couple share dessert by candlelight at a waterfront table, the illuminated towers behind them.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null, focal: null, aperture: null,
        light: 'Candlelight', time: '20:00', location: 'Waterfront table', cast: 'Couple',
        wardrobe: null, composition: null, style: STYLE, colour: grade(null),
        params: '2:3 master, adshel in the ad system.'
      }
    },
    {
      // slides 59, 63
      id: 'w06-family', src: 'assets/img/gallery/w06-family-lifestyle.jpg', w: 1539, h: 1216,
      world: 'W06', worldName: 'Luxury Living', pillar: 'Exceptional Hospitality', hour: '22:00', h24: 22,
      title: 'Family lifestyle', channel: 'Key visual', audience: 'Residents, tourists', echo: ECHO.bronzeOxford,
      alt: 'An Emirati family at home at night: the father pours from a dallah while the mother and children sit together on a sofa, the lit skyline in the window behind.',
      fields: {
        prompt: null, model: ROUTE_PEOPLE, camera: null, lens: null,
        focal: '35mm, interior (the read)', aperture: null, light: 'Lamp-lit', time: '22:00',
        location: 'Residence at night', cast: 'The Emirati family (character sheet)', wardrobe: null,
        composition: null, style: STYLE, colour: grade(ECHO.bronzeOxford.name), params: '3:2 master.'
      }
    }
  ];

  // Labels in the order the record reads.
  window.AMI_FIELDS = [
    ['prompt', 'Final generation prompt'],
    ['model', 'AI model'],
    ['camera', 'Camera reference'],
    ['lens', 'Lens'],
    ['focal', 'Focal length'],
    ['aperture', 'Aperture'],
    ['light', 'Lighting direction'],
    ['time', 'Time of day'],
    ['location', 'Location / environment'],
    ['cast', 'Cast / character reference'],
    ['wardrobe', 'Wardrobe direction'],
    ['composition', 'Composition'],
    ['style', 'Photography style'],
    ['colour', 'Colour treatment'],
    ['params', 'Parameters & references']
  ];
})();
