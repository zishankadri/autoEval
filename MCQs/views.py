from django.shortcuts import render, redirect, HttpResponse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages

import shutil
import os
import json
from .forms import TestQuestionForm
from .models import Question, Test, CorrectAnswerList, TestQuestion, Note
from core.models import Klass, Student
from courses.models import Chapter
from . import mcq_auto_scanner

from .AIQuestionGenerator import make_notes

def mcqs(request):
    test_list = Test.objects.filter(klass__user=request.user)
    klasses = Klass.objects.filter(user=request.user)
    
    if request.method == "POST":
        test_name = request.POST['test-name']
        no_of_questions= request.POST['no-of-questions']
        klass_id = request.POST['select-class']
        chapter_id = request.POST['select-chapter']
        answer_sheet_type = request.POST['select-sheet-type']
        is_public = request.POST['is_public']
        print("hello yolo ")
        # return redirect(f"/mcqs/")
        return redirect(f"/mcqs/create_test/{klass_id}/{test_name}/{no_of_questions}/{answer_sheet_type}/{is_public}/{chapter_id}")


    context = {
        'test_list': test_list,
        'klasses': klasses,

    }
    return render(request, "MCQs/mcqs.html", context)


def create_test(request, klass_id, test_name, no_of_questions, answer_sheet_type, is_public, chapter_id):
    klass = Klass.objects.get(id=klass_id)
    try:
        chapter = Chapter.objects.get(id=chapter_id)
    except:
        chapter = None

    QuestionFormset = formset_factory(TestQuestionForm, extra=int(no_of_questions))

    if request.method == "POST":
        formset = QuestionFormset(request.POST)

        if formset.is_valid():
            # Create a new test
            test = Test(
                name=test_name,
                klass=klass,
                answer_sheet_type=answer_sheet_type,
                no_of_questions=no_of_questions
            )
            test.save()

            # Create & add all questions to the test
            for i, form in enumerate(formset):
                test_question = form.save(commit=False)
                test_question.test = test
                test_question.order = i
                test_question.save()
                test.selected_questions.add(test_question)

            return redirect(f"/mcqs/download_test/{test.id}/")

    formset = QuestionFormset()
    # Fetch questions of level and subject to recommend & like/dislike
    if chapter:
        recommended_questions = Question.objects.filter(
            # test__klass__user__subject=request.user.subject,
            # test__klass__level=klass.level,
            chapter=chapter,
            is_public=True
        )
    else:
        recommended_questions = Question.objects.filter(
            subject=request.user.subject,
            level=klass.level,
            is_public=True
        )
        recommended_questions = Question.objects.all()

        print(recommended_questions)

    context = {
        'formset': formset,
        'recommended_questions': recommended_questions,
    }

    return render(request, "MCQs/create_test.html", context)


def delete_test(request, test_id):
    test = Test.objects.get(id=test_id)
    test.delete()
    return redirect("/mcqs/")
    

def download_test(request, test_id):
    test = Test.objects.get(id=test_id)
    question_list = TestQuestion.objects.filter(test=test).order_by("order")
    student_list = Student.objects.filter(klass=test.klass)

    if test.rendered_html:
        #  If the client is downloading the same test twice.
        return HttpResponse(test.rendered_html)
    print(test.rendered_html)
    
    if test.answer_sheet_type == "UNIQUE_TEST":
        if CorrectAnswerList.objects.filter(test=test).exists():
            return redirect("/mcqs/")

        for student in student_list:
            new_list = CorrectAnswerList(test=test, student=student)
            new_list.save()

    elif test.answer_sheet_type == "SAME_TEST":
        if not test.simple_answer_list:
            # return redirect("/mcqs/")

            for question in question_list:
                test.simple_answer_list += question.correct_ans
            test.save()

    context = {
        'test': test,
        'question_list': question_list,
        'student_list': student_list,
    }

    rendered_html = render(request, "MCQs/download_test.html", context)
    test.rendered_html = rendered_html.content.decode('utf-8')
    test.save()
    return rendered_html


def checkout_test(request, test_id):
    test = Test.objects.get(id=test_id)

    if request.method == "POST":
        if test.status != test.RUNNING:
            return HttpResponse(request, "This test is undergoing analysis.")
        
        main_inputs_folder = os.path.join(settings.MEDIA_ROOT, "inputs")
        main_outputs_folder = os.path.join(settings.MEDIA_ROOT, "outputs")
    
        # Create a input and output directory specificaly for this test result
        input_folder = os.path.join(main_inputs_folder, f"input-{test.id}")
        output_folder = os.path.join(main_outputs_folder, f"output-{test.id}")

        if 'file' in request.FILES:
            uplaoded_answersheets = request.FILES.getlist('file')
            for answersheet in uplaoded_answersheets:
                input_folder = os.path.join(main_inputs_folder, f"input-{test.id}")
                file_path = os.path.join(input_folder, answersheet.name)
                default_storage.save(file_path, answersheet)
                print("✅ File saved at:", file_path)

        elif "generate_grades" in request.POST:
            try:
                # If no answer sheets are uploaded to scan
                if not os.path.isdir(input_folder):
                    messages.error(request, "No answer sheets are uploaded to scan.")
                    return render(request, "MCQs/upload_answer_sheets.html", {'test': test})
                    
                test.status = test.ANALIZING
                test.save()

                data = mcq_auto_scanner.scan(test, input_folder, output_folder)


                if not data:
                    raise "Analization failed"
                print(data)

                test.distribute_scores(data)
                test.status = test.COMPLETED
                test.save()
                # Create personalized notes for each student
                make_notes(test)

                messages.success(request, "The correction is complete, and the notes are accessible in the classes section.")
            except:
                messages.error(request, "Something went wrong. Please check your input and make sure this is the correct test.")
                test.status = test.RUNNING
                test.save()
                # Remove the temporary folders
                if os.path.exists(input_folder): shutil.rmtree(input_folder)
                if os.path.exists(output_folder): shutil.rmtree(output_folder)

    context = {
        'test': test,
    }

    if test.status == test.COMPLETED:
        notes = Note.objects.filter(test=test)
        context['notes'] = notes
        return render(request, "MCQs/completed_test.html", context)

    return render(request, "MCQs/upload_answer_sheets.html", context)

from django.shortcuts import get_object_or_404
import re
def download_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    text_content = re.sub(r'\\n', '\n', note.notes)  
    response = HttpResponse(text_content, content_type="text/plain")
    response["Content-Disposition"] = f"attachment; filename='{note.student}_{note.test}_Notes.txt'"
    return response

# APIs
@login_required
@csrf_exempt
def like_question(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        question_id = data.get('question_id', '')

        if question_id:
            question = Question.objects.get(id=question_id)
            if request.user not in question.likes.all() and request.user not in question.dislikes.all():
                question.likes.add(request.user)
            elif request.user not in question.likes.all():
                question.likes.add(request.user)
                question.dislikes.remove(request.user)
                question.save()
                return JsonResponse({'user_disliked_previously': True}, status=200)
            else:
                question.likes.remove(request.user)
            question.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({'error': f'id and name are required'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


@login_required
@csrf_exempt
def dislike_question(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        question_id = data.get('question_id', '')

        if question_id:
            question = Question.objects.get(id=question_id)
            if request.user not in question.dislikes.all() and request.user not in question.likes.all():
                question.dislikes.add(request.user)
            elif request.user not in question.dislikes.all():
                question.dislikes.add(request.user)
                question.likes.remove(request.user)
                question.save()
                return JsonResponse({'user_liked_previously': True}, status=200)
            else:
                question.dislikes.remove(request.user)
            question.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({'error': f'id and name are required'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

    # if test.answer_sheet_type == "UNIQUE_TEST":
    #     final_list = {}
    #     shuffled_questions = list(question_list)
    #     random.shuffle(shuffled_questions)
    #     for question in shuffled_questions:
    #         shuffled_answers = [question.ans_a, question.ans_b, question.ans_c, question.ans_d]
    #         random.shuffle(shuffled_answers)
    #         final_list[question.question] = shuffled_answers

    #     print("Final list: ", final_list)
