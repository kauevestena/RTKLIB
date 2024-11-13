static double prectrop(gtime_t time, const double *pos, const double *azel,
                       const prcopt_t *opt, const double *x, double *dtdx,
                       double *var)
{
    const double zazel[] = {0.0, PI / 2.0};
    double zhd, m_h, m_w, cotz, grad_n, grad_e;

    /* zenith hydrostatic delay */
    zhd = tropmodel(time, pos, zazel, 0.0);

    /* mapping function */
    m_h = tropmapf(time, pos, azel, &m_w);

    double m_w_orig = m_w;

    if ((opt->tropopt == TROPOPT_ESTG || opt->tropopt == TROPOPT_CORG) && azel[1] > 0.0)
    {

        /* m_w=m_0+m_0*cot(el)*(Gn*cos(az)+Ge*sin(az)): ref [6] */
        cotz = 1.0 / tan(azel[1]);
        grad_n = m_w * cotz * cos(azel[0]);
        grad_e = m_w * cotz * sin(azel[0]);
        m_w += grad_n * x[1] + grad_e * x[2];
        dtdx[1] = grad_n * (x[0] - zhd);
        dtdx[2] = grad_e * (x[0] - zhd);
    }
    dtdx[0] = m_w;
    *var = SQR(0.01);

    /* getting current delay path, to be written in the output file */
    FILE *infileStream;
    char fileText[200];

    infileStream = fopen("/home/RTKLIB/curr_delaypath.txt", "r");
    fgets(fileText, 200, infileStream);
    fclose(infileStream);

    double final_delay = m_h * zhd + m_w * (x[0] - zhd);

    FILE *fout;

    fout = fopen(fileText, "a+");

    /* "grad_e,grad_n,m_h,m_w_orig,m_w,zhd,zwd,x_0,x_1,x_2,tot_delay" */

    fprintf(fout, "%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n", grad_e, grad_n, m_h, m_w_orig, m_w, zhd, x[0] - zhd, x[0], x[1], x[2], final_delay);

    fclose(fout);

    return final_delay;
}