package com.fishsauce.app;

import android.content.Context;
import android.widget.TextView;

import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.assertEquals;

@RunWith(RobolectricTestRunner.class)
public class SayHelloTest {

    private TextView txtHello;
    private TextView txtHelp;
    private SayHelloActivity sayHello;

    @Before
    public void setUp() {
        Context context = ApplicationProvider.getApplicationContext();
        txtHello = new TextView(context);
        txtHelp = new TextView(context);
        txtHello.setText("Hi");
        sayHello = new SayHelloActivity();
    }

    @Test
    public void start_typesFullText_afterAdvancingFakeTime() {
        sayHello.start(txtHello, txtHelp);

        ShadowLooper.idleMainLooper(2 * 80 + 500 + 10, TimeUnit.MILLISECONDS);

        assertEquals("Hi", txtHello.getText().toString());
        assertEquals(View.VISIBLE, txtHelp.getVisibility());
    }

    @Test
    public void txtHelp_stillInvisible_rightAfterLastChar() {
        sayHello.start(txtHello, txtHelp);

        ShadowLooper.idleMainLooper(2 * 80 + 10, TimeUnit.MILLISECONDS);

        assertEquals("Hi", txtHello.getText().toString());
        assertEquals(View.INVISIBLE, txtHelp.getVisibility());
    }
}
