from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.ai import AIHistory, ChatHistory
from app.services.ai_service import AIService, PROMPT_TEMPLATES
from app.services.workspace_ai import WorkspaceAI
from app.services.translation_service import translate_text

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/workspace')
@login_required
def workspace():
    """Main AI Workspace suite rendering the six AI tools and prompt templates."""
    active_tool = request.args.get('tool', 'caption')
    if active_tool not in {'caption', 'script', 'hashtag', 'bio', 'rewrite', 'seo'}:
        active_tool = 'caption'

    # Prompt-template arrows use normal navigation instead of fragile inline
    # tab clicks. This guarantees the correct tool opens even when Bootstrap's
    # modal/tab JavaScript is unavailable or another click handler intercepts it.
    template_id = (request.args.get('template_id') or '').strip()
    template_tool_map = {
        'tpl_viral_hook': 'script',
        'tpl_insta_story': 'caption',
        'tpl_youtube_intro': 'script',
        'tpl_linkedin_thought': 'rewrite',
        'tpl_bio_creator': 'bio',
        'tpl_thread_post': 'caption',
        'tpl_seo_blog': 'seo',
        'tpl_podcast_script': 'script',
    }
    selected_template = next((tpl for tpl in PROMPT_TEMPLATES if tpl.get('id') == template_id), None)
    if selected_template:
        active_tool = template_tool_map.get(template_id, active_tool)

    recent_history = AIHistory.query.filter_by(user_id=current_user.id).order_by(AIHistory.created_at.desc()).limit(30).all()
    return render_template('ai/workspace.html', 
                           active_tool=active_tool, 
                           templates=PROMPT_TEMPLATES,
                           recent_history=recent_history,
                           selected_template=selected_template)

@ai_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """Generate Workspace content with Gemini/OpenAI, with the old local service as fallback."""
    data = request.get_json() or {}
    tool_type = data.get('tool_type', 'caption')
    if tool_type not in {'caption', 'script', 'hashtag', 'bio', 'rewrite', 'seo'}:
        return jsonify({'success': False, 'error': f'Invalid tool type: {tool_type}'}), 400

    language = current_user.language or 'English'
    previous_output = (data.get('previous_output') or '').strip()

    defaults = {
        'caption': {'topic': 'Content Creation', 'platform': 'Instagram', 'tone': 'Engaging'},
        'script': {'topic': 'AI Tools', 'format': 'Reels / Shorts', 'length': '60 Seconds', 'audience': 'Content Creators'},
        'hashtag': {'topic': 'Digital Marketing', 'platform': 'Instagram', 'niche': ''},
        'bio': {'niche': 'Content Creator', 'personality': 'Witty', 'cta': 'Download Free Guide'},
        'rewrite': {'content': '', 'style': 'Engaging & Persuasive'},
        'seo': {'topic': 'Creator OS', 'industry': 'Creator Economy'},
    }
    payload = {**defaults[tool_type], **data}

    try:
        response_text, tokens_used, provider = WorkspaceAI.generate(
            tool_type, payload, language, previous_output=previous_output
        )
        response_text = AIService.clean_generated_output(response_text)

        if tool_type == 'rewrite':
            prompt_text = f"Content: {payload.get('content', '')[:120]}... | Style: {payload.get('style', '')}"
        elif tool_type == 'script':
            prompt_text = f"Topic: {payload.get('topic')} | Format: {payload.get('format')} | Length: {payload.get('length')}"
        elif tool_type == 'hashtag':
            prompt_text = f"Topic: {payload.get('topic')} | Platform: {payload.get('platform')} | Niche: {payload.get('niche')}"
        elif tool_type == 'bio':
            prompt_text = f"Niche: {payload.get('niche')} | Personality: {payload.get('personality')} | CTA: {payload.get('cta')}"
        elif tool_type == 'seo':
            prompt_text = f"SEO Keywords for: {payload.get('topic')} | Industry: {payload.get('industry')}"
        else:
            prompt_text = f"Topic: {payload.get('topic')} | Platform: {payload.get('platform')} | Tone: {payload.get('tone')}"

        history_entry = AIHistory(
            user_id=current_user.id,
            tool_type=tool_type,
            prompt=prompt_text,
            response=response_text,
            tokens_used=tokens_used
        )
        db.session.add(history_entry)
        db.session.commit()

        return jsonify({
            'success': True,
            'id': history_entry.id,
            'tool_type': tool_type,
            'response': response_text,
            'tokens_used': tokens_used,
            'provider': provider,
            'created_at': history_entry.created_at.strftime('%H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@ai_bp.route('/refine', methods=['POST'])
@login_required
def refine():
    """Refine the current Workspace result with the real LLM provider."""
    data = request.get_json() or {}
    previous_output = (data.get('previous_output') or '').strip()
    instruction = (data.get('instruction') or '').strip()
    tool_type = data.get('tool_type', 'caption')
    if not previous_output or not instruction:
        return jsonify({'success': False, 'error': 'Please provide the previous result and your follow-up request.'}), 400

    language = current_user.language or 'English'
    prompt_data = {
        'content': previous_output,
        'topic': previous_output,
        'style': instruction,
        'question': instruction,
        'current_output': previous_output,
        'current_tool': tool_type,
    }
    try:
        response_text, tokens_used, provider = WorkspaceAI.generate(
            'rewrite', prompt_data, language, previous_output=previous_output
        )
        response_text = AIService.clean_generated_output(response_text)
        history_entry = AIHistory(
            user_id=current_user.id,
            tool_type=tool_type,
            prompt=f"Follow-up: {instruction}",
            response=response_text,
            tokens_used=tokens_used
        )
        db.session.add(history_entry)
        db.session.commit()
        return jsonify({
            'success': True,
            'id': history_entry.id,
            'tool_type': tool_type,
            'response': response_text,
            'tokens_used': tokens_used,
            'provider': provider,
            'created_at': history_entry.created_at.strftime('%H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_bp.route('/copilot', methods=['POST'])
@login_required
def copilot():
    """Free-form CreatorOS creative assistant.

    The chat is intentionally not limited to button-like commands. The user can start
    from a blank workspace, refer to earlier messages, ask for ideas, reject a result,
    change direction, or request a rewrite. The service uses the selected tool as its
    working mode and keeps the latest generated content as the immediate context.
    """
    data = request.get_json() or {}
    question = (data.get('question') or '').strip()
    history = data.get('history') or []
    current_output = (data.get('current_output') or '').strip()
    current_tool = (data.get('current_tool') or 'caption').strip().lower()
    current_context = data.get('current_context') or {}
    lang = current_user.language or 'English'

    if not question:
        return jsonify({'answer': _copilot_text(lang, 'empty')})

    # The chat can generate from scratch. It is no longer disabled until a button-based
    # generation happens first.
    try:
        response_text, answer, tokens_used, provider = WorkspaceAI.chat(
            question=question,
            language=lang,
            current_output=current_output,
            current_tool=current_tool,
            context=current_context,
            history=history,
        )
        response_text = AIService.clean_generated_output(response_text)
        answer = AIService.clean_generated_output(answer)

        history_entry = AIHistory(
            user_id=current_user.id,
            tool_type=current_tool,
            prompt=f"Workspace chat: {question}",
            response=response_text,
            tokens_used=tokens_used,
        )
        db.session.add(history_entry)
        db.session.commit()

        return jsonify({
            'answer': answer,
            'updated_output': response_text,
            'id': history_entry.id,
            'tool_type': current_tool,
            'created_at': history_entry.created_at.strftime('%H:%M:%S'),
            'provider': provider,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'answer': _copilot_text(lang, 'error') + f' ({e})'}), 500


def _copilot_text(lang, key):
    """Keep assistant replies in the selected interface language for supported UI languages."""
    texts = {
        'English': {
            'empty':'Ask me something about CreatorOS.', 'updated':'Done — I updated the current result in the main output area.',
            'error':'I could not update the current result. Please try again.',
                    'language':'Open Profile Settings → Language Selection. Choose a language; the CreatorOS interface uses that language while English remains the default.',
            'photo':'Open Profile Settings and click the camera icon on the circular avatar. Choose an image; the page previews the photo and saves it.',
            'caption':'Caption Generator creates a caption from your topic, platform, and tone. After generating, use this same conversation bar to make it shorter, more professional, change the hook, or recreate it.',
            'script':'Script Generator creates short-form, YouTube long-form, or podcast scripts. Generate first, then use this conversation bar for changes.',
            'hashtag':'Hashtag Generator creates hashtags from topic, platform, and niche. Generate first, then ask me to add, remove, or change them.',
            'bio':'Bio Generator creates profile bio variations from niche, personality, and CTA.',
            'seo':'SEO Keywords generates keyword ideas and an SEO report from the topic and industry.',
            'calendar':'Calendar is where you schedule and manage content dates and statuses.',
            'draft':'Draft Manager stores drafts, and its Recycle Bin handles deleted drafts.',
            'image':'Images & Thumbnails handles visual generation and thumbnail work. Media & Assets manages uploaded files.',
            'video':'Video Editor handles clips, trimming, audio, filters, merging, preview, and MP4 export.',
            'analytics':'Analytics shows the performance information available in your CreatorOS account.',
            'profile':'Profile Settings controls your display name, profile photo, language, and password.',
            'help':'I can explain CreatorOS features and help you operate its tools. Ask about captions, scripts, hashtags, SEO, profile, language, calendar, video editing, or say “recreate this” after generating a result.',
            'fallback':'I can help with CreatorOS features and workflows. Tell me what you are trying to do, for example “make this caption shorter”, “how do I change the language?”, or “where is the video editor?”'
        },
        'Kannada': {
            'empty':'CreatorOS ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಿ.', 'updated':'ಮುಗಿಯಿತು — ಮುಖ್ಯ ಫಲಿತಾಂಶದ ಭಾಗದಲ್ಲೇ ಪ್ರಸ್ತುತ ಫಲಿತಾಂಶವನ್ನು ನವೀಕರಿಸಿದ್ದೇನೆ.',
            'error':'ಪ್ರಸ್ತುತ ಫಲಿತಾಂಶವನ್ನು ನವೀಕರಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
            'language':'ಪ್ರೊಫೈಲ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳಿಗೆ ಹೋಗಿ → ಭಾಷೆ ಆಯ್ಕೆ ಮಾಡಿ. ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿದಾಗ CreatorOS ಇಂಟರ್‌ಫೇಸ್ ಅದೇ ಭಾಷೆಯಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ. ಇಂಗ್ಲಿಷ್ ಡೀಫಾಲ್ಟ್ ಆಗಿರುತ್ತದೆ.',
            'photo':'ಪ್ರೊಫೈಲ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳಿಗೆ ಹೋಗಿ ಮತ್ತು ವೃತ್ತಾಕಾರದ ಪ್ರೊಫೈಲ್ ಚಿತ್ರದ ಕ್ಯಾಮೆರಾ ಐಕಾನ್ ಒತ್ತಿ. ಚಿತ್ರ ಆಯ್ಕೆ ಮಾಡಿದ ನಂತರ ಅದೇ ಪುಟದಲ್ಲಿ ಚಿತ್ರ ಕಾಣಿಸುತ್ತದೆ ಮತ್ತು ಉಳಿಸಲಾಗುತ್ತದೆ.',
            'caption':'ಕ್ಯಾಪ್ಶನ್ ಜನರೇಟರ್ ವಿಷಯ, ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ ಮತ್ತು ಬರವಣಿಗೆಯ ಶೈಲಿಯಿಂದ ಕ್ಯಾಪ್ಶನ್ ರಚಿಸುತ್ತದೆ. ರಚಿಸಿದ ನಂತರ ಇದೇ ಸಂಭಾಷಣೆಯಲ್ಲಿ ಚಿಕ್ಕದಾಗಿ, ವೃತ್ತಿಪರವಾಗಿ, ಹೊಸ ಹುಕ್‌ನೊಂದಿಗೆ ಅಥವಾ ಹೊಸ ಆವೃತ್ತಿಯಾಗಿ ಕೇಳಬಹುದು.',
            'script':'ಸ್ಕ್ರಿಪ್ಟ್ ಜನರೇಟರ್ ಶಾರ್ಟ್ ವೀಡಿಯೋ, ಯೂಟ್ಯೂಬ್ ದೀರ್ಘ ವೀಡಿಯೋ ಅಥವಾ ಪಾಡ್‌ಕಾಸ್ಟ್ ಸ್ಕ್ರಿಪ್ಟ್ ರಚಿಸುತ್ತದೆ. ಮೊದಲು ರಚಿಸಿ, ನಂತರ ಇದೇ ಸಂಭಾಷಣೆಯಲ್ಲಿ ಬದಲಾವಣೆ ಕೇಳಿ.',
            'hashtag':'ಹ್ಯಾಶ್‌ಟ್ಯಾಗ್ ಜನರೇಟರ್ ವಿಷಯ, ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ ಮತ್ತು ಕ್ರಿಯೇಟರ್ ಕ್ಷೇತ್ರದ ಆಧಾರದ ಮೇಲೆ ಹ್ಯಾಶ್‌ಟ್ಯಾಗ್ ರಚಿಸುತ್ತದೆ. ಸೇರಿಸಲು, ತೆಗೆದುಹಾಕಲು ಅಥವಾ ಬದಲಾಯಿಸಲು ಇದೇ ಸಂಭಾಷಣೆಯಲ್ಲಿ ಕೇಳಿ.',
            'bio':'ಬಯೋ ಜನರೇಟರ್ ನಿಮ್ಮ ಕ್ಷೇತ್ರ, ವ್ಯಕ್ತಿತ್ವ ಮತ್ತು ಕರೆ-ಟು-ಆಕ್ಷನ್ ಆಧರಿಸಿ ಪ್ರೊಫೈಲ್ ಬಯೋ ರೂಪಾಂತರಗಳನ್ನು ರಚಿಸುತ್ತದೆ.',
            'seo':'SEO ಕೀವರ್ಡ್‌ಗಳು ವಿಷಯ ಮತ್ತು ಉದ್ಯಮದ ಆಧಾರದ ಮೇಲೆ ಕೀವರ್ಡ್‌ಗಳು ಮತ್ತು SEO ವರದಿ ರಚಿಸುತ್ತದೆ.',
            'calendar':'ಕ್ಯಾಲೆಂಡರ್‌ನಲ್ಲಿ ವಿಷಯದ ದಿನಾಂಕಗಳು ಮತ್ತು ಪ್ರಕಟಣೆ ಸ್ಥಿತಿಗಳನ್ನು ಯೋಜಿಸಿ ಮತ್ತು ನಿರ್ವಹಿಸಬಹುದು.',
            'draft':'ಡ್ರಾಫ್ಟ್ ಮ್ಯಾನೇಜರ್‌ನಲ್ಲಿ ಡ್ರಾಫ್ಟ್‌ಗಳನ್ನು ಸಂಗ್ರಹಿಸಬಹುದು. ಅಳಿಸಿದ ಡ್ರಾಫ್ಟ್‌ಗಳಿಗೆ ರಿಸೈಕಲ್ ಬಿನ್ ಇದೆ.',
            'image':'ಚಿತ್ರಗಳು ಮತ್ತು ಥಂಬ್‌ನೇಲ್‌ಗಳು ದೃಶ್ಯ ರಚನೆ ಮತ್ತು ಥಂಬ್‌ನೇಲ್ ಕೆಲಸಕ್ಕೆ. ಮೀಡಿಯಾ ಮತ್ತು ಆಸ್ತಿಗಳು ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಫೈಲ್‌ಗಳನ್ನು ನಿರ್ವಹಿಸುತ್ತದೆ.',
            'video':'ವೀಡಿಯೋ ಎಡಿಟರ್ ಕ್ಲಿಪ್‌ಗಳು, ಟ್ರಿಮ್, ಆಡಿಯೋ, ಫಿಲ್ಟರ್, ವಿಲೀನ, ಪೂರ್ವವೀಕ್ಷಣೆ ಮತ್ತು MP4 ರಫ್ತು ನಿರ್ವಹಿಸುತ್ತದೆ.',
            'analytics':'ಅನಾಲಿಟಿಕ್ಸ್ ನಿಮ್ಮ CreatorOS ಖಾತೆಯಲ್ಲಿ ಲಭ್ಯವಿರುವ ಕಾರ್ಯಕ್ಷಮತೆಯ ಮಾಹಿತಿಯನ್ನು ತೋರಿಸುತ್ತದೆ.',
            'profile':'ಪ್ರೊಫೈಲ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳಲ್ಲಿ ಹೆಸರು, ಪ್ರೊಫೈಲ್ ಚಿತ್ರ, ಭಾಷೆ, ಥೀಮ್ ಮತ್ತು ಪಾಸ್‌ವರ್ಡ್ ಬದಲಾಯಿಸಬಹುದು.',
            'help':'ನಾನು CreatorOS ವೈಶಿಷ್ಟ್ಯಗಳು ಮತ್ತು ಕಾರ್ಯವಿಧಾನಗಳನ್ನು ವಿವರಿಸಬಹುದು. ವ್ಯಾಕರಣ, ಕ್ಯಾಪ್ಶನ್, ಸ್ಕ್ರಿಪ್ಟ್, ಹ್ಯಾಶ್‌ಟ್ಯಾಗ್, SEO, ಪ್ರೊಫೈಲ್, ಭಾಷೆ, ಕ್ಯಾಲೆಂಡರ್ ಅಥವಾ ವೀಡಿಯೋ ಎಡಿಟಿಂಗ್ ಬಗ್ಗೆ ಕೇಳಿ. ಫಲಿತಾಂಶ ಇಷ್ಟವಾಗದಿದ್ದರೆ “ಇದನ್ನು ಮತ್ತೆ ರಚಿಸಿ” ಎಂದು ಹೇಳಿ.',
            'fallback':'ನಾನು CreatorOS ವೈಶಿಷ್ಟ್ಯಗಳು ಮತ್ತು ಕಾರ್ಯವಿಧಾನಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು. ನೀವು ಏನು ಮಾಡಲು ಪ್ರಯತ್ನಿಸುತ್ತಿದ್ದೀರಿ ಎಂದು ಹೇಳಿ — ಉದಾಹರಣೆಗೆ “ಈ ಕ್ಯಾಪ್ಶನ್ ಚಿಕ್ಕದಾಗಿ ಮಾಡಿ” ಅಥವಾ “ಭಾಷೆಯನ್ನು ಹೇಗೆ ಬದಲಾಯಿಸಬೇಕು?” ಎಂದು ಕೇಳಿ.'
        },
        'Telugu': {
            'empty':'CreatorOS గురించి ఏదైనా అడగండి.', 'updated':'పూర్తయింది — ప్రధాన ఫలితాల భాగంలోనే ప్రస్తుత ఫలితాన్ని నవీకరించాను.',
            'error':'ప్రస్తుత ఫలితాన్ని నవీకరించలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.',
            'language':'ప్రొఫైల్ సెట్టింగ్స్ → భాష ఎంపికకు వెళ్లండి. భాషను ఎంచుకున్న తర్వాత CreatorOS ఇంటర్‌ఫేస్ అదే భాషలో కనిపిస్తుంది. ఇంగ్లీష్ డిఫాల్ట్‌గా ఉంటుంది.',
            'photo':'ప్రొఫైల్ సెట్టింగ్స్‌కి వెళ్లి వృత్తాకార ప్రొఫైల్ ఫోటోపై ఉన్న కెమెరా ఐకాన్‌ను నొక్కండి. ఫోటో ఎంచుకున్న వెంటనే అదే పేజీలో కనిపిస్తుంది మరియు సేవ్ అవుతుంది.',
            'caption':'క్యాప్షన్ జనరేటర్ విషయం, ప్లాట్‌ఫారమ్ మరియు టోన్ ఆధారంగా క్యాప్షన్ తయారు చేస్తుంది. తయారు చేసిన తర్వాత ఇదే సంభాషణలో చిన్నగా, ప్రొఫెషనల్‌గా, కొత్త హుక్‌తో లేదా కొత్త వెర్షన్‌గా మార్చమని అడగవచ్చు.',
            'script':'స్క్రిప్ట్ జనరేటర్ షార్ట్ వీడియో, యూట్యూబ్ లాంగ్‌ఫార్మ్ లేదా పాడ్‌కాస్ట్ స్క్రిప్ట్ తయారు చేస్తుంది. ముందుగా తయారు చేసి, తర్వాత ఇదే సంభాషణలో మార్పులు అడగండి.',
            'hashtag':'హ్యాష్‌ట్యాగ్ జనరేటర్ విషయం, ప్లాట్‌ఫారమ్ మరియు క్రియేటర్ నిచ్ ఆధారంగా హ్యాష్‌ట్యాగ్‌లను తయారు చేస్తుంది. వాటిని జోడించమని, తీసేయమని లేదా మార్చమని ఇదే సంభాషణలో అడగండి.',
            'bio':'బయో జనరేటర్ నిచ్, వ్యక్తిత్వం మరియు CTA ఆధారంగా ప్రొఫైల్ బయోలను తయారు చేస్తుంది.',
            'seo':'SEO కీవర్డ్స్ విషయం మరియు పరిశ్రమ ఆధారంగా కీవర్డ్ సూచనలు మరియు SEO రిపోర్ట్ తయారు చేస్తుంది.',
            'calendar':'క్యాలెండర్‌లో కంటెంట్ తేదీలు మరియు ప్రచురణ స్థితులను ప్లాన్ చేసి నిర్వహించవచ్చు.',
            'draft':'డ్రాఫ్ట్ మేనేజర్‌లో డ్రాఫ్ట్‌లను నిర్వహించవచ్చు. తొలగించిన డ్రాఫ్ట్‌ల కోసం రీసైకిల్ బిన్ ఉంటుంది.',
            'image':'చిత్రాలు & థంబ్‌నెయిల్స్ విజువల్ జనరేషన్ మరియు థంబ్‌నెయిల్ పనికి. మీడియా & ఆస్తులు అప్‌లోడ్ చేసిన ఫైళ్లను నిర్వహిస్తుంది.',
            'video':'వీడియో ఎడిటర్ క్లిప్‌లు, ట్రిమ్, ఆడియో, ఫిల్టర్లు, విలీనం, ప్రివ్యూ మరియు MP4 ఎక్స్‌పోర్ట్‌ను నిర్వహిస్తుంది.',
            'analytics':'అనలిటిక్స్ మీ CreatorOS ఖాతాలో అందుబాటులో ఉన్న పనితీరు సమాచారాన్ని చూపిస్తుంది.',
            'profile':'ప్రొఫైల్ సెట్టింగ్స్‌లో పేరు, ప్రొఫైల్ ఫోటో, భాష, థీమ్ మరియు పాస్‌వర్డ్‌ను మార్చవచ్చు.',
            'help':'నేను CreatorOS ఫీచర్లు మరియు విధానాలను వివరించగలను. వ్యాకరణం, క్యాప్షన్, స్క్రిప్ట్, హ్యాష్‌ట్యాగ్, SEO, ప్రొఫైల్, భాష, క్యాలెండర్ లేదా వీడియో ఎడిటింగ్ గురించి అడగండి. ఫలితం నచ్చకపోతే “దీన్ని మళ్లీ తయారు చేయి” అని చెప్పండి.',
            'fallback':'నేను CreatorOS ఫీచర్లు మరియు వర్క్‌ఫ్లోల్లో సహాయం చేయగలను. మీరు ఏమి చేయాలనుకుంటున్నారో చెప్పండి — ఉదాహరణకు “ఈ క్యాప్షన్‌ను చిన్నగా చేయి” లేదా “భాషను ఎలా మార్చాలి?” అని అడగండి.'
        }
    }
    return texts.get(lang, texts['English']).get(key, texts['English'].get(key, 'I can help with CreatorOS.'))

@ai_bp.route('/chatbot')
@login_required
def chatbot():
    """CreatorOS Hub chat screen."""
    recent_chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at.desc()).limit(20).all()
    return render_template('ai/chatbot.html', recent_chats=recent_chats)

@ai_bp.route('/chatbot/message', methods=['POST'])
@login_required
def chatbot_message():
    """Process a CreatorOS Hub message."""
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'success': False, 'error': 'Please enter a message.'}), 400

    try:
        response = AIService.clean_generated_output(AIService.chat(message))
        history_entry = ChatHistory(user_id=current_user.id, message=message, response=response)
        db.session.add(history_entry)
        db.session.commit()
        return jsonify({
            'success': True,
            'response': response,
            'history': {
                'id': history_entry.id,
                'message': history_entry.message,
                'response': history_entry.response,
                'created_at': history_entry.created_at.strftime('%b %d, %Y - %H:%M')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_bp.route('/chatbot/history/<int:history_id>')
@login_required
def chatbot_history_item(history_id):
    record = ChatHistory.query.filter_by(id=history_id, user_id=current_user.id).first_or_404()
    return jsonify({'success': True, 'message': record.message, 'response': record.response})

@ai_bp.route('/chatbot/history/clear', methods=['POST'])
@login_required
def clear_chatbot_history():
    ChatHistory.query.filter_by(user_id=current_user.id).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True})



@ai_bp.route('/history/data')
@login_required
def history_data():
    """Return the signed-in user's saved AI Workspace history for the modal."""
    records = AIHistory.query.filter_by(user_id=current_user.id).order_by(AIHistory.created_at.desc()).all()
    return jsonify({'records': [record.to_dict() for record in records]})

@ai_bp.route('/history')
@login_required
def history():
    """Filterable AI history and favorites list."""
    tool_filter = request.args.get('tool', 'all')
    favorites_only = request.args.get('favorites', 'false').lower() == 'true'

    query = AIHistory.query.filter_by(user_id=current_user.id)
    if tool_filter != 'all':
        query = query.filter_by(tool_type=tool_filter)
    if favorites_only:
        query = query.filter_by(is_favorite=True)

    records = query.order_by(AIHistory.created_at.desc()).all()
    return render_template('ai/history.html', 
                           records=records, 
                           tool_filter=tool_filter, 
                           favorites_only=favorites_only)

@ai_bp.route('/favorite/<int:history_id>', methods=['POST'])
@login_required
def toggle_favorite(history_id):
    """Toggles favorite status for an AI history record."""
    record = AIHistory.query.filter_by(id=history_id, user_id=current_user.id).first_or_404()
    record.is_favorite = not record.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': record.is_favorite})

@ai_bp.route('/delete/<int:history_id>', methods=['POST'])
@login_required
def delete_history(history_id):
    """Deletes an AI history entry."""
    record = AIHistory.query.filter_by(id=history_id, user_id=current_user.id).first_or_404()
    db.session.delete(record)
    db.session.commit()
    flash("AI Workspace: the selected history item was deleted.", "info")
    return redirect(url_for('ai.history'))
