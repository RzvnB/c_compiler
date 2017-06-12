struct Pt{
	int x,y;
};

struct Pt points[20/4+5];
int n;

int	count(int k)
{
	// int x = 5;
	int n;
	int		i;
	for(i=n=0;i<10;i=i+1) {
		if(points[i].x>=0&&points[i].y>=0)
			n=n+1;
	}

	n = i + 1;
	return n;
}



double abs(double x)
{
	if(x<0) {
		return -x;
	}
		return x;
}

void main()
{
	char v[10];
	put_s(v);
	count(n);
}
