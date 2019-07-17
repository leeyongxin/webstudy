
from django.http import JsonResponse
from django.shortcuts import HttpResponse
import matplotlib.pyplot as plt
import datetime
import random
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_agg import FigureCanvasAgg
import base64
import io



def test_data(request):
    data = {"a":1}
    return JsonResponse(data)

def getimage1(request, pk):
    print(pk)
    pk = int(pk)
    # Construct the graph
    def pic1():
        fig, ax = plt.subplots()
        x=[]
        y=[]
        now=datetime.datetime.now()
        delta=datetime.timedelta(days=1)
        for i in range(10):
            x.append(now)
            now+=delta
            y.append(random.randint(0, 1000))
        ax.plot_date(x, y, '-')
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        canvas=FigureCanvasAgg(fig)
        buf = io.BytesIO()
        #plt.savefig(buf, format='png')
        canvas.print_png(buf)
        #plt.close(fig)
        ret = {}
        #ret['inline_png']= base64.b64encode(buf.getvalue()) for python3, need to add decode
        ret['inline_png']= base64.b64encode(buf.getvalue()).decode()
        response=HttpResponse(buf.getvalue(),content_type='image/png')
        return JsonResponse({"p1":ret['inline_png']})
    
    def pic2():
        return JsonResponse({"p1":"I'm 2"})
    
    fdict = dict(enumerate((pic1, pic2)))
    ret = fdict[pk]()
    return ret
    #return render(request, 'wind/pic.html', ret)